#!/usr/bin/env python3
"""
Générateur de vidéos de graphiques animés - Style Flourish
Crée des visualisations animées avec transitions fluides
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
import seaborn as sns
from datetime import datetime, timedelta
import random
import os

# Configuration du style
plt.style.use('dark_background')
sns.set_palette("husl")

class AnimatedChartGenerator:
    def __init__(self, figsize=(12, 8), dpi=100):
        self.figsize = figsize
        self.dpi = dpi
        self.fig = None
        self.ax = None
        
    def generate_sample_data(self, chart_type="bar_race"):
        """Génère des données d'exemple selon le type de graphique"""
        if chart_type == "bar_race":
            return self._generate_bar_race_data()
        elif chart_type == "line_growth":
            return self._generate_line_data()
        elif chart_type == "scatter_evolution":
            return self._generate_scatter_data()
        elif chart_type == "pie_transition":
            return self._generate_pie_data()
    
    def _generate_bar_race_data(self):
        """Génère des données pour un bar chart race"""
        categories = ['Tech', 'Finance', 'Santé', 'Éducation', 'Commerce', 'Industrie']
        dates = pd.date_range('2020-01-01', '2024-01-01', freq='Q')
        
        data = []
        base_values = {cat: random.randint(50, 200) for cat in categories}
        
        for date in dates:
            for cat in categories:
                # Variation aléatoire avec tendance
                growth = random.uniform(-0.05, 0.15)
                base_values[cat] *= (1 + growth)
                data.append({
                    'date': date,
                    'category': cat,
                    'value': max(0, base_values[cat])
                })
        
        return pd.DataFrame(data)
    
    def _generate_line_data(self):
        """Génère des données pour graphique linéaire"""
        dates = pd.date_range('2020-01-01', '2024-01-01', freq='M')
        companies = ['Apple', 'Google', 'Microsoft', 'Amazon', 'Tesla']
        
        data = []
        for company in companies:
            values = np.cumsum(np.random.randn(len(dates)) * 10 + 5) + random.randint(100, 500)
            for date, value in zip(dates, values):
                data.append({
                    'date': date,
                    'company': company,
                    'value': max(0, value)
                })
        
        return pd.DataFrame(data)
    
    def _generate_scatter_data(self):
        """Génère des données pour scatter plot évolutif"""
        dates = pd.date_range('2020-01-01', '2024-01-01', freq='Q')
        countries = ['France', 'Allemagne', 'Italie', 'Espagne', 'UK', 'Suède']
        
        data = []
        for date in dates:
            for country in countries:
                gdp = random.uniform(20000, 50000) + np.random.randn() * 2000
                happiness = random.uniform(5, 8) + np.random.randn() * 0.3
                population = random.uniform(10, 80)
                
                data.append({
                    'date': date,
                    'country': country,
                    'gdp': gdp,
                    'happiness': happiness,
                    'population': population
                })
        
        return pd.DataFrame(data)
    
    def _generate_pie_data(self):
        """Génère des données pour graphique circulaire évolutif"""
        categories = ['Desktop', 'Mobile', 'Tablet', 'TV', 'Autres']
        dates = pd.date_range('2020-01-01', '2024-01-01', freq='6M')
        
        data = []
        for date in dates:
            # Simulation de l'évolution mobile vs desktop
            mobile_growth = (date.year - 2020) * 0.05
            values = [
                max(5, 45 - mobile_growth * 10),  # Desktop décroît
                min(65, 35 + mobile_growth * 10), # Mobile croît
                max(3, 15 - mobile_growth * 2),   # Tablet décroît
                min(8, 3 + mobile_growth),        # TV croît
                2                                 # Autres stable
            ]
            
            for cat, val in zip(categories, values):
                data.append({
                    'date': date,
                    'category': cat,
                    'value': val
                })
        
        return pd.DataFrame(data)
    
    def create_bar_race_animation(self, data, output_file="bar_race.mp4", duration=10):
        """Crée une animation bar chart race"""
        fig, ax = plt.subplots(figsize=self.figsize, facecolor='black')
        ax.set_facecolor('black')
        
        dates = sorted(data['date'].unique())
        colors = plt.cm.Set3(np.linspace(0, 1, len(data['category'].unique())))
        color_map = dict(zip(data['category'].unique(), colors))
        
        def animate(frame):
            ax.clear()
            ax.set_facecolor('black')
            
            current_date = dates[frame]
            current_data = data[data['date'] == current_date].sort_values('value', ascending=True)
            
            # Barres horizontales
            bars = ax.barh(range(len(current_data)), current_data['value'], 
                          color=[color_map[cat] for cat in current_data['category']])
            
            # Labels et styling
            ax.set_yticks(range(len(current_data)))
            ax.set_yticklabels(current_data['category'], color='white', fontsize=12)
            ax.set_xlabel('Valeur', color='white', fontsize=14)
            ax.set_title(f'Évolution par secteur - {current_date.strftime("%Y-%m")}', 
                        color='white', fontsize=16, pad=20)
            
            # Valeurs sur les barres
            for i, (bar, value) in enumerate(zip(bars, current_data['value'])):
                ax.text(value + max(current_data['value']) * 0.01, i, 
                       f'{value:.0f}', va='center', color='white', fontweight='bold')
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.tick_params(colors='white')
            
            plt.tight_layout()
        
        anim = animation.FuncAnimation(fig, animate, frames=len(dates), 
                                     interval=duration*1000//len(dates), repeat=True)
        
        # Sauvegarde
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=15, metadata=dict(artist='ChartGenerator'), bitrate=1800)
        anim.save(output_file, writer=writer, dpi=self.dpi)
        plt.close()
        
        return output_file
    
    def create_line_growth_animation(self, data, output_file="line_growth.mp4", duration=10):
        """Crée une animation de croissance linéaire"""
        fig, ax = plt.subplots(figsize=self.figsize, facecolor='black')
        ax.set_facecolor('black')
        
        dates = sorted(data['date'].unique())
        companies = data['company'].unique()
        colors = plt.cm.tab10(np.linspace(0, 1, len(companies)))
        
        def animate(frame):
            ax.clear()
            ax.set_facecolor('black')
            
            end_date = dates[frame]
            current_data = data[data['date'] <= end_date]
            
            for i, company in enumerate(companies):
                company_data = current_data[current_data['company'] == company]
                if len(company_data) > 0:
                    ax.plot(company_data['date'], company_data['value'], 
                           color=colors[i], linewidth=3, label=company, marker='o', markersize=4)
            
            ax.set_title(f'Évolution des valeurs - {end_date.strftime("%Y-%m")}', 
                        color='white', fontsize=16, pad=20)
            ax.set_xlabel('Date', color='white', fontsize=14)
            ax.set_ylabel('Valeur', color='white', fontsize=14)
            ax.legend(facecolor='black', edgecolor='white', labelcolor='white')
            ax.grid(True, alpha=0.3, color='white')
            
            # Styling
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.tick_params(colors='white')
            
            plt.tight_layout()
        
        anim = animation.FuncAnimation(fig, animate, frames=len(dates), 
                                     interval=duration*1000//len(dates), repeat=True)
        
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=15, metadata=dict(artist='ChartGenerator'), bitrate=1800)
        anim.save(output_file, writer=writer, dpi=self.dpi)
        plt.close()
        
        return output_file
    
    def create_scatter_evolution(self, data, output_file="scatter_evolution.mp4", duration=10):
        """Crée une animation scatter plot évolutif"""
        fig, ax = plt.subplots(figsize=self.figsize, facecolor='black')
        ax.set_facecolor('black')
        
        dates = sorted(data['date'].unique())
        countries = data['country'].unique()
        colors = plt.cm.tab10(np.linspace(0, 1, len(countries)))
        color_map = dict(zip(countries, colors))
        
        def animate(frame):
            ax.clear()
            ax.set_facecolor('black')
            
            current_date = dates[frame]
            current_data = data[data['date'] == current_date]
            
            scatter = ax.scatter(current_data['gdp'], current_data['happiness'], 
                               s=current_data['population']*5, 
                               c=[color_map[country] for country in current_data['country']], 
                               alpha=0.7, edgecolors='white', linewidth=1)
            
            # Labels pour chaque point
            for _, row in current_data.iterrows():
                ax.annotate(row['country'], (row['gdp'], row['happiness']), 
                           xytext=(5, 5), textcoords='offset points', 
                           color='white', fontsize=10, fontweight='bold')
            
            ax.set_title(f'PIB vs Bonheur - {current_date.strftime("%Y")}', 
                        color='white', fontsize=16, pad=20)
            ax.set_xlabel('PIB par habitant', color='white', fontsize=14)
            ax.set_ylabel('Indice de bonheur', color='white', fontsize=14)
            ax.grid(True, alpha=0.3, color='white')
            
            # Styling
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.tick_params(colors='white')
            
            plt.tight_layout()
        
        anim = animation.FuncAnimation(fig, animate, frames=len(dates), 
                                     interval=duration*1000//len(dates), repeat=True)
        
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=15, metadata=dict(artist='ChartGenerator'), bitrate=1800)
        anim.save(output_file, writer=writer, dpi=self.dpi)
        plt.close()
        
        return output_file

def main():
    """Fonction principale pour générer les animations"""
    generator = AnimatedChartGenerator()
    
    print("🎬 Génération des graphiques animés...")
    
    # 1. Bar Chart Race
    print("📊 Création du Bar Chart Race...")
    bar_data = generator.generate_sample_data("bar_race")
    bar_file = generator.create_bar_race_animation(bar_data, "bar_race_animation.mp4")
    print(f"✅ Bar Race créé: {bar_file}")
    
    # 2. Line Growth Animation
    print("📈 Création de l'animation linéaire...")
    line_data = generator.generate_sample_data("line_growth")
    line_file = generator.create_line_growth_animation(line_data, "line_growth_animation.mp4")
    print(f"✅ Animation linéaire créée: {line_file}")
    
    # 3. Scatter Evolution
    print("🎯 Création du scatter évolutif...")
    scatter_data = generator.generate_sample_data("scatter_evolution")
    scatter_file = generator.create_scatter_evolution(scatter_data, "scatter_evolution.mp4")
    print(f"✅ Scatter évolutif créé: {scatter_file}")
    
    print("\n🎉 Toutes les animations ont été générées avec succès!")
    print("📁 Fichiers créés:")
    print("   - bar_race_animation.mp4")
    print("   - line_growth_animation.mp4") 
    print("   - scatter_evolution.mp4")

if __name__ == "__main__":
    # Vérification des dépendances
    try:
        import matplotlib
        import pandas
        import numpy
        import seaborn
        print("✅ Toutes les dépendances sont installées")
        main()
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("📦 Installez avec: pip install matplotlib pandas numpy seaborn")