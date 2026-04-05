import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler


class TechnologyOpportunityAnalyzer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.trained = False

    def train_model(self, training_data):
        # training_data: list of dicts with features and opportunity_score
        df = pd.DataFrame(training_data)
        features = df.drop('opportunity_score', axis=1)
        target = df['opportunity_score']

        features_scaled = self.scaler.fit_transform(features)
        self.model.fit(features_scaled, target)
        self.trained = True

    def evaluate_opportunity(self, patent_features):
        if not self.trained:
            # Default evaluation based on heuristics
            score = self._heuristic_evaluation(patent_features)
        else:
            features_df = pd.DataFrame([patent_features])
            features_scaled = self.scaler.transform(features_df)
            score = self.model.predict(features_scaled)[0]

        return {
            'score': float(score),
            'level': self._classify_opportunity(score),
            'recommendations': self._generate_recommendations(patent_features, score)
        }

    def _heuristic_evaluation(self, features):
        # Simple heuristic: based on citation count, novelty, market potential
        score = 0
        score += features.get('citation_count', 0) * 0.1
        score += features.get('novelty_score', 5) * 0.2
        score += features.get('market_potential', 5) * 0.3
        score += features.get('technical_maturity', 5) * 0.2
        score += features.get('competitive_density', 10) * -0.1  # Negative factor
        return min(max(score, 0), 10)

    def _classify_opportunity(self, score):
        if score >= 8:
            return 'High'
        elif score >= 6:
            return 'Medium'
        elif score >= 4:
            return 'Low'
        else:
            return 'Very Low'

    def _generate_recommendations(self, features, score):
        recommendations = []
        if score < 5:
            recommendations.append("Consider improving technical novelty")
        if features.get('competitive_density', 0) > 7:
            recommendations.append("High competition in this area, consider differentiation")
        if features.get('market_potential', 0) > 7:
            recommendations.append("High market potential, prioritize development")
        if features.get('technical_maturity', 0) < 5:
            recommendations.append("Technology is immature, more R&D needed")
        return recommendations


def analyze_technology_opportunities(patents_data):
    analyzer = TechnologyOpportunityAnalyzer()
    results = []
    for patent in patents_data:
        # Extract features from patent data
        features = {
            'citation_count': patent.get('citation_count', 0),
            'novelty_score': patent.get('novelty_score', 5),  # Placeholder
            'market_potential': patent.get('market_potential', 5),  # Placeholder
            'technical_maturity': patent.get('technical_maturity', 5),  # Placeholder
            'competitive_density': patent.get('competitive_density', 5),  # Placeholder
        }
        opportunity = analyzer.evaluate_opportunity(features)
        results.append({
            'patent_id': patent.get('id'),
            'title': patent.get('title'),
            **opportunity
        })
    return results
