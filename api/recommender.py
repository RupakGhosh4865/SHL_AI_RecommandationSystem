"""
Core Recommendation Engine
Uses Gemini AI + Simple Similarity Search
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict
import google.generativeai as genai
from api.models import AssessmentItem

logger = logging.getLogger(__name__)


class AssessmentRecommender:
    """
    Assessment recommendation system using:
    - Simple keyword matching for initial filtering
    - Gemini AI for intelligent ranking and explanation
    """
    
    def __init__(self, data_path: str, gemini_api_key: str):
        """
        Initialize the recommender system
        
        Args:
            data_path: Path to cleaned CSV file
            gemini_api_key: Google Gemini API key
        """
        logger.info("Initializing AssessmentRecommender...")
        
        # Load assessment data
        self.df = pd.read_csv(data_path, encoding='utf-8')
        logger.info(f"Loaded {len(self.df)} assessments")
        
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Gemini AI configured")
        
        # Prepare data
        self._prepare_data()
        
    def _prepare_data(self):
        """Prepare assessment data for recommendations"""
        # Fill NaN values
        self.df = self.df.fillna('')
        
        # Create searchable text (lowercase for matching)
        self.df['search_text'] = (
            self.df['name'].astype(str) + ' ' +
            self.df['description'].astype(str) + ' ' +
            self.df['category_final'].astype(str) + ' ' +
            self.df['combined_text'].astype(str)
        ).str.lower()
        
        logger.info("Data preparation complete")
    
    def _keyword_search(self, query: str, top_k: int = 20) -> List[int]:
        """
        Simple keyword-based search to find relevant assessments
        
        Args:
            query: User query
            top_k: Number of candidates to return
            
        Returns:
            List of assessment indices sorted by relevance
        """
        query_lower = query.lower()
        keywords = [w for w in query_lower.split() if len(w) > 2]
        
        # Score each assessment
        scores = []
        for idx, row in self.df.iterrows():
            score = 0
            text = row['search_text']
            name = row['name'].lower()
            
            # Count keyword matches
            for keyword in keywords:
                score += text.count(keyword) * 2
                score += name.count(keyword) * 5  # Name matches weighted higher
            
            if score > 0:
                scores.append((idx, score))
        
        # Sort by score and return top K indices
        scores.sort(key=lambda x: x[1], reverse=True)
        return [idx for idx, score in scores[:top_k]]
    
    def _format_assessment(self, row: pd.Series) -> AssessmentItem:
        """
        Format a DataFrame row into AssessmentItem
        
        Args:
            row: DataFrame row
            
        Returns:
            AssessmentItem matching API response format
        """
        # Parse test_type - convert to list if string
        test_type = row.get('category_final', 'Other')
        if isinstance(test_type, str):
            test_type = [test_type] if test_type else ['Other']
        
        # Extract duration (convert to int)
        duration = row.get('duration_minutes', 0)
        if pd.isna(duration):
            duration = 0
        else:
            try:
                duration = int(duration)
            except:
                duration = 0
        
        # Get adaptive and remote support
        adaptive = row.get('adaptive', '')
        remote = row.get('remote_testing', '')
        
        # Format as Yes/No
        adaptive_support = "Yes" if 'yes' in str(adaptive).lower() else "No"
        remote_support = "Yes" if 'yes' in str(remote).lower() else "No"
        
        # Get description
        description = row.get('description', '')
        if not description or len(str(description)) < 10:
            description = row.get('combined_text', '')
        description = str(description).strip()
        
        # Truncate description to reasonable length
        if len(description) > 200:
            description = description[:197] + "..."
        
        return AssessmentItem(
            url=str(row.get('url', '')),
            name=str(row.get('name', '')),
            adaptive_support=adaptive_support,
            description=description,
            duration=duration,
            remote_support=remote_support,
            test_type=test_type
        )
    
    def _rank_with_gemini(self, query: str, candidates: List[AssessmentItem], top_k: int = 10) -> List[AssessmentItem]:
        """
        Use Gemini AI to intelligently rank candidates
        
        Args:
            query: User query
            candidates: List of candidate assessments
            top_k: Number of final recommendations
            
        Returns:
            Ranked list of top K assessments
        """
        if not candidates:
            return []
        
        # Prepare context for Gemini
        context = "AVAILABLE ASSESSMENTS:\n\n"
        for i, assessment in enumerate(candidates[:15], 1):  # Limit to 15 for token efficiency
            context += f"{i}. {assessment.name}\n"
            context += f"   Category: {', '.join(assessment.test_type)}\n"
            context += f"   Duration: {assessment.duration} minutes\n"
            context += f"   Description: {assessment.description[:100]}...\n\n"
        
        # Create ranking prompt
        prompt = f"""You are an expert HR consultant. Rank these assessments for this job requirement.

JOB REQUIREMENT:
{query}

{context}

TASK:
Return ONLY the numbers (1-{len(candidates[:15])}) of the top {min(top_k, len(candidates))} most relevant assessments, in order of relevance.
Format: Just the numbers separated by commas, nothing else.

Example response: 3,7,1,5,2

Your response:"""
        
        try:
            # Get Gemini's ranking
            response = self.model.generate_content(prompt)
            ranking_text = response.text.strip()
            
            # Parse the rankings
            rankings = []
            for num_str in ranking_text.replace('\n', ',').split(','):
                try:
                    num = int(num_str.strip()) - 1  # Convert to 0-indexed
                    if 0 <= num < len(candidates[:15]):
                        rankings.append(num)
                except:
                    continue
            
            # If we got valid rankings, reorder candidates
            if rankings:
                ranked = [candidates[i] for i in rankings[:top_k]]
                # Add remaining candidates if needed
                used_indices = set(rankings[:top_k])
                remaining = [c for i, c in enumerate(candidates) if i not in used_indices]
                ranked.extend(remaining[:top_k - len(ranked)])
                return ranked[:top_k]
        
        except Exception as e:
            logger.warning(f"Gemini ranking failed: {e}, using original order")
        
        # Fallback: return original order
        return candidates[:top_k]
    
    def recommend(self, query: str, top_k: int = 10) -> List[AssessmentItem]:
        """
        Get top K assessment recommendations for a query
        
        Args:
            query: Job description or query string
            top_k: Number of recommendations to return (max 10)
            
        Returns:
            List of AssessmentItem objects
        """
        logger.info(f"Getting recommendations for: '{query[:50]}...'")
        
        # Step 1: Keyword search to find candidates
        candidate_indices = self._keyword_search(query, top_k=20)
        
        if not candidate_indices:
            logger.warning("No matching assessments found")
            return []
        
        logger.info(f"Found {len(candidate_indices)} candidate assessments")
        
        # Step 2: Format candidates
        candidates = []
        for idx in candidate_indices:
            try:
                assessment = self._format_assessment(self.df.iloc[idx])
                candidates.append(assessment)
            except Exception as e:
                logger.error(f"Error formatting assessment {idx}: {e}")
                continue
        
        # Step 3: Rank with Gemini AI
        ranked_results = self._rank_with_gemini(query, candidates, top_k=top_k)
        
        logger.info(f"Returning {len(ranked_results)} recommendations")
        return ranked_results
    
    def get_statistics(self) -> Dict:
        """Get statistics about the loaded assessments"""
        return {
            "total_assessments": len(self.df),
            "categories": self.df['category_final'].value_counts().to_dict(),
            "assessments_with_duration": int(self.df['duration_minutes'].notna().sum()),
            "remote_enabled": int((self.df['remote_testing'].str.contains('yes', case=False, na=False)).sum()),
            "adaptive_enabled": int((self.df['adaptive'].str.contains('yes', case=False, na=False)).sum())
        }