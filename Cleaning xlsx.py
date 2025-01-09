import os
import pandas as pd


def remove_duplicates_and_clean_excel(folder_path):
    """
    Removes duplicates and rows with blank or 0 values from all Excel files in the specified folder.

    Args:
        folder_path (str): Path to the folder containing Excel files.

    Returns:
        None
    """
    # Loop through all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing file: {file_name}")

            try:
                # Read the Excel file
                df = pd.read_excel(file_path)

                # Remove duplicates
                df_cleaned = df.drop_duplicates()

                # Remove rows with blank or 0 values
                df_cleaned = df_cleaned.replace("", pd.NA)  # Replace blank strings with NaN
                df_cleaned = df_cleaned.dropna(how='any')  # Drop rows with any NaN values
                df_cleaned = df_cleaned[(df_cleaned != 0).all(axis=1)]  # Drop rows with any 0 values

                # Define the output folder
                cleaned_folder_path = os.path.join("Cleaned" + folder_path)
                if not os.path.exists(cleaned_folder_path):
                    os.makedirs(cleaned_folder_path)

                # Define the output file path
                cleaned_file_path = os.path.join(cleaned_folder_path, f"{os.path.splitext(file_name)[0]}_cleaned.xlsx")

                # Save the cleaned DataFrame to a new Excel file
                df_cleaned.to_excel(cleaned_file_path, index=False)

                print(f"Cleaned file saved as: {cleaned_file_path}")
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")


folder = 'search_backups'

remove_duplicates_and_clean_excel(folder)
