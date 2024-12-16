# -*- coding: utf-8 -*-
"""Final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-r1qOhNN3PT2GVHd0TJBXuIbkMGGPcaG
"""
import streamlit as st

st.title('My Final Project!')
st.subheader('Marshal Wang')
st.write('December 16, 2024')

# **Introduction:**
st.subheader("Introduction")
st.write(
    "Working on this project blasting Lady Gaga, I reflect on the thousands of songs I've listened to over the course of my life. "
    "The music industry has always fascinated me, especially the seemingly random process through which certain songs achieve massive popularity while others, seemingly just as deserving, fade into obscurity. "
    "I have a strong upbringing in classical music, listening to Beethoven, Mozart, and the likes. From that, it's fairly intuitive to me why certain songs resonate through the ages: they sound good. However, in today's modern world, I'm not so certain what affects popularity."
)

st.write(
    "I wanted to explore one question: Is a song's popularity primarily determined by its intrinsic musical qualities, or is it largely a matter of luck, timing, artist brand, or other external factors? By delving into the raw data of music, looking at factors such as the genre, the 'lyricism,' tempo, and many classifications under the song, I hope to find evidence of a trend."
)

# **Data Description:**
st.subheader("Data Description")
st.write(
    "The data I have chosen to use for this project is sourced from the TidyTuesday Spotify dataset, available in CSV format. The dataset provides detailed information about various songs on Spotify, including their musical attributes, popularity scores, and genre classifications."
)

st.write(
    "This dataset contains a deeply comprehensive 32,833 rows of songs and over 20 columns detailing their musical attributes and metadata. Key features include numerical values such as danceability, energy, and loudness, as well as categorical features like genre. By leveraging these attributes, this project seeks to uncover the extent to which a song's intrinsic musical characteristics influence its popularity."
)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import sklearn.metrics as metrics
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.inspection import permutation_importance

# Load Data
df = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-01-21/spotify_songs.csv')

st.subheader("Dataset Preview")
st.dataframe(df.head())

st.subheader("Data Exploration")

st.write("### Max Popularity Song")
st.dataframe(df[df['track_popularity'] == 100])

st.write("### Least Popular Songs")
st.dataframe(df[df['track_popularity'] == 0].head())

st.write("### Distribution of Track Popularity")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['track_popularity'], bins=df['track_popularity'].nunique(), kde=True, ax=ax)
ax.set_title('Distribution of Track Popularity')
ax.set_xlabel('Track Popularity')
ax.set_ylabel('Frequency')
st.pyplot(fig)

st.write(
    "We quickly see a major trend here: a vast majority of the data lies in the 0-5 popularity zone: likely due to joke songs, and noisy uploads into Spotify which don't necesarily have the best applicability in the scheme of the data. More importantly, we can see that outside of this huge tail, this is a fairly normally distributed data with a mean of approximately 50."
)

# Cleaning noisy data
df_filtered = df[~df['track_popularity'].isin([0, 1, 2, 3, 4, 5])]

st.write("### Distribution After Cleaning")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df_filtered['track_popularity'], bins=df_filtered['track_popularity'].nunique(), kde=True, ax=ax)
ax.set_title('Distribution of Track Popularity (0 through 5 removed)')
ax.set_xlabel('Track Popularity')
ax.set_ylabel('Frequency')
st.pyplot(fig)

st.write(
    "Upon removing the first 5 data points which would most likely confound our data, it becomes much more normally distributed. However, it is important to note that having songs in the top 10 percentile is exceedingly rare and seems to be up to chance more than anything."
)

# Filter out songs with low popularity scores
df['is_rap'] = (df['playlist_genre'] == 'rap').astype(int)
df['is_pop'] = (df['playlist_genre'] == 'pop').astype(int)
df['is_rock'] = (df['playlist_genre'] == 'rock').astype(int)

#Drop playlist column
df.describe()

# Create my features variable
features = ['danceability', 'energy', 'speechiness', 'acousticness', 'valence']+['is_rap', 'is_pop', 'is_rock']

X = df[features]
y = df['track_popularity']

# Split the data into training and testing sets. I chose to sue the standard test sample of 20% and random state of 42
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalize the data to ensure models like KNN have the best opportunity to succeed
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

"""For my baseline model, I chose to use a mean effectively implying no correlation between the two. Further, I chose to use mean squared error or MSE as my benchmark of the "best" model."""

# Baseline Model
baseline_prediction = np.mean(df['track_popularity'])
baseline_mse = mean_squared_error(y_test, [baseline_prediction] * len(y_test))
baseline_r2 = r2_score(y_test, [baseline_prediction] * len(y_test))

print(f"Baseline Model - MSE: {baseline_mse}")

"""The implied MSE of 418 is quite high, but that's to be expected. Looking next at the linear regression, this is a very simple regression and unlikely to work. While it may not capture the full complexity of the data, it establishes a clear baseline for comparison against more advanced models.

"""

#Linear Regression
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Linear Regression Model - MSE: {mse}")

# Feature Importance
feature_importance = pd.DataFrame({'Feature': features, 'Importance': abs(model.coef_)})
feature_importance = feature_importance.sort_values(by='Importance', ascending=False)
feature_importance

"""Unfortunately our MSE is not significantly improved, however, we do gain some interesting insights through the feature importance. The leading factor is not a necessarily an innate musical feature but rather whether or not if it is in the pop genre. Our decreased MSE is not to be unexpected, it's to be exected that many different factors affect the popularity of asong and to an extent, they also affect each other. For instance, being in the pop genre would imply a certain level of lyricism.

Next is the random forest model. I have the highest hope for this model given the seemingly non-linear relationship between the variables and the popularity variable. Random Forest effectively models complex, non-linear relationship so therefore, this shoudl yield a better result.
"""

# Random Forest Model
rf_model = RandomForestRegressor(random_state=42, n_estimators=100)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)

rf_mse = mean_squared_error(y_test, y_pred_rf)
rf_r2 = r2_score(y_test, y_pred_rf)

print(f"Random Forest - MSE: {rf_mse}")
# Feature Importance using coefficients
feature_importance_rf = pd.DataFrame({'Feature': X.columns, 'Importance': rf_model.feature_importances_})
feature_importance_rf = feature_importance_rf.sort_values(by='Importance', ascending=False)
print("\nFeature Importance (Random Forest):")
feature_importance_rf

"""As we predicted, the MSE is *significantly* lower than any other model. The Random Forest model highlights that audio attributes, especially acousticness, speechiness, and valence, are the strongest predictors of track_popularity, contrary to every other model. Binary genre features contribute minimally, suggesting that song characteristics outweigh genre classification in determining popularity. This is particularly interesting given how different of a result it provdies compared to every single other model. Overall, this was the most successful model out of all and was most capable of predicting accurately."""

# Initialize and train a KNN regressor model
knn_model = KNeighborsRegressor(n_neighbors=50)
knn_model.fit(X_train, y_train)

# Make predictions on the test set
y_pred_knn = knn_model.predict(X_test)

# Evaluate the model
mse_knn = mean_squared_error(y_test, y_pred_knn)
print(f"KNN Mean Squared Error: {mse_knn}")

# Feature importance
perm = permutation_importance(knn_model, X_test, y_test, n_repeats=30, random_state=42)
pd.DataFrame({'Feature': X.columns, 'Importance': perm.importances_mean})

"""The results for KNN were disappointing. KNN’s high MSE even compared to the baseline and regression, and low feature importance values indicate that it is not well-suited for this particular dataset and the many confounding variables that exist. The lack of localized patterns most likely hindered this model's performance. The struggle to generalize really hurt."""

tree_model = DecisionTreeRegressor(random_state=42, max_depth=4)
tree_model.fit(X_train, y_train)

# Make predictions on the test set
y_pred_tree = tree_model.predict(X_test)

# Evaluate the model
mse_tree = mean_squared_error(y_test, y_pred_tree)
print(f"Decision Tree Mean Squared Error: {mse_tree}")

# Plot the decision tree
plt.figure(figsize=(20, 10))
plot_tree(tree_model, filled=True, feature_names=X.columns, rounded=True)
plt.show()

feature_importance_tree = pd.DataFrame({'Feature': X.columns, 'Importance': tree_model.feature_importances_})
feature_importance_tree = feature_importance_tree.sort_values(by='Importance', ascending=False)
print("\nFeature Importance (Decision Tree):")
feature_importance_tree

"""The MSE for the decision tree was in the same ball park as the other models, outside of RFM.  One key issue is the reliance on a small number of dominant features, particularly acousticness and is_pop, while completely ignoring others like speechiness, valence, and is_rap. This overemphasis on a few features probably led to overfitting, where the model performed well on the training set but failed to generalize on the test set.

# **Conclusion:**
In this analysis, we explored various predictive models—including Linear Regression, Multiple Regression, Random Forest, K-Nearest Neighbors (KNN), and Decision Tree—to understand what factors might influence a song's popularity. While none of the models produced exceptionally low MSEs, this outcome aligns with the initial expectations of the project. Predicting song popularity is inherently complex, as external factors like marketing, cultural influence, and artist fame play a significant role—elements that cannot be captured purely through numerical and genre-based features. While the models themselves were not great at predicting the popularity of the songs, we were able to very rouhgly figure out what might aid.

However, a couple key factors did appear. **Acousticness and danceability** were particularly strong in relation to the other factors when conducitng feature importance, with stronger correlation with popularity, particularly in the Decision Tree and Random Forest models. Further, being a **pop song**, while weak as an absolute measure, stood out amongst all genres that were tested. This alings rather strongly with general sentiment on music today.

On a broader level, I learned the importance of balancing model complexity with interpretability. Random Forest consistently outperformed others, demonstrating the power of ensemble methods to capture non-linear relationships, while simpler models like Linear Regression established a baseline for comparison.

# **Next Steps:**
I've always enjoyed music for the actual intrinsic values, however, when looking at modern popular music obviously other factors must come into play. I hope to examine more external variables such as artist recognition, playlist placements, streaming counts, and release date trends in a future project. These would more likley be stronger predictive factors than the intrinsic factors we looked at today.

Further, I think looking on a time horizon such as analyzing how popularity changes over time by incorporating release year or weekly streaming trends could be really interesting, and seeing what sparks the interest in a song. A time-series analysis could capture evolving audience preferences and seasonal effects.

Lastly, I think I want to simplify this project: I had many, many variables throughout the whole project which really made modeling and predicting quite difficult. Down the road, maybe looking at one artist, or songs from one period and analyzing what qualities make them attractive would trul be able to provide strong predictive power.

# **Final Thoughts**
From a learning perspective, this was easily the most complex project I've had to do, combining everythign we've learned over the last year and trying to extrapolate that into this project. While my results unfortunately didn't create the idealized beautiful model that I hoped to have made, it did confirm my initial suspicions which is just as good of a result in my eyes and I deeply enjoyed the process of figuring out the answer to my hypothesis. Overall, I'm excited to acutally expand on this project over the winter and hopefully find some interesting results within the music space!
"""
