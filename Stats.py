import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load all .xlsx files from the folder 'Cleanedsearch_backups'
folder_path = 'Cleanedsearch_backups/'  # Adjust if necessary
files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

# Step 2: Combine all data into a single dataframe
all_data = pd.DataFrame()
for file in files:
    file_path = os.path.join(folder_path, file)
    print(f"Reading file: {file_path}")
    try:
        df = pd.read_excel(file_path)
        print(f"File read successfully with {len(df)} rows.")
        all_data = pd.concat([all_data, df], ignore_index=True)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

if all_data.empty:
    print("No data loaded. Please check the input files and folder path.")
else:
    # Step 3: Clean the 'price' column
    if 'price' in all_data.columns:
        all_data['price'] = all_data['price'].replace({'\$': '', ',': ''}, regex=True)
        all_data['price'] = pd.to_numeric(all_data['price'], errors='coerce')
        all_data = all_data.dropna(subset=['price'])
    else:
        print("Column 'price' not found in the data.")

    # Step 4: Perform analysis
    print(all_data.info())
    print(all_data.describe())
    print(all_data.isnull().sum())

    if 'airline' in all_data.columns:
        airline_price = all_data.groupby('airline')['price'].mean().sort_values(ascending=False)
        print(airline_price)

    # Step 5: Visualization

    # Price Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(all_data['price'], bins=30, kde=True)
    plt.title('Price Distribution')
    plt.xlabel('Price')
    plt.ylabel('Frequency')
    plt.show()

    # Average Price per Airline
    if 'airline' in all_data.columns:
        plt.figure(figsize=(12, 8))
        sns.barplot(x=airline_price.index, y=airline_price.values, palette="viridis")
        plt.xticks(rotation=45)
        plt.title('Average Price by Airline')
        plt.xlabel('Airline')
        plt.ylabel('Average Price')
        plt.show()

    # Distribution of Stops
    if 'stops' in all_data.columns:
        plt.figure(figsize=(10, 6))
        sns.countplot(data=all_data, x='stops', palette="coolwarm")
        plt.title('Distribution of Stops')
        plt.xlabel('Number of Stops')
        plt.ylabel('Frequency')
        plt.show()

    # Price vs. Duration
    if 'duration' in all_data.columns:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=all_data, x='duration', y='price', hue='stops', palette="husl")
        plt.title('Price vs. Duration')
        plt.xlabel('Duration')
        plt.ylabel('Price')
        plt.legend(title='Stops')
        plt.show()

    # Average Price by Day of the Week
    if 'day' in all_data.columns:
        day_price = all_data.groupby('day')['price'].mean().sort_values()
        plt.figure(figsize=(12, 6))
        sns.barplot(x=day_price.index, y=day_price.values, palette="pastel")
        plt.title('Average Price by Day of the Week')
        plt.xlabel('Day')
        plt.ylabel('Average Price')
        plt.show()

    # Average Price by Time of the Day
    if 'time' in all_data.columns:
        time_price = all_data.groupby('time')['price'].mean().sort_values()
        plt.figure(figsize=(12, 6))
        sns.pointplot(x=time_price.index, y=time_price.values, color='blue', markers='o', linestyles='-')
        plt.title('Average Price by Time of the Day')
        plt.xlabel('Time')
        plt.ylabel('Average Price')
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.show()

    # Route Analysis (From-To)
    if 'from' in all_data.columns and 'to' in all_data.columns:
        top_routes = all_data.groupby(['from', 'to']).size().reset_index(name='count').sort_values(by='count', ascending=False).head(10)
        plt.figure(figsize=(12, 6))
        sns.barplot(data=top_routes, x='count', y=top_routes.apply(lambda row: f"{row['from']} → {row['to']}", axis=1), palette="Blues_d")
        plt.title('Top 10 Routes by Frequency')
        plt.xlabel('Number of Flights')
        plt.ylabel('Route')
        plt.show()
