# -*- coding: utf-8 -*-
"""app.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18Xhjrb9N_eU2W05F0TwoNog5LwsV_AOH
"""

# Commented out IPython magic to ensure Python compatibility.
# app.py
import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Copy your existing code here

def main():
    st.title("Disk Usage Analysis Dashboard")

    # Add Streamlit components and code here based on your needs

    st.sidebar.header("Navigation")
    selected_page = st.sidebar.radio(
        "Select Page", ["Home", "Unit Analysis", "Total Analysis"]
    )

    if selected_page == "Home":
        st.header("Welcome to the Disk Usage Analysis Dashboard!")
        # Add content for the home page

    elif selected_page == "Unit Analysis":
        st.header("Unit Analysis")

    # Import Library

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    import warnings
    #import skfuzzy as fuzz

    warnings.filterwarnings('ignore')

    from pandas.plotting import lag_plot
    from sklearn.metrics import mean_squared_error
    from sklearn.metrics import mean_absolute_error
    from statsmodels.tools.eval_measures import mse, rmse,meanabs
    from statsmodels.graphics.tsaplots import  month_plot,quarter_plot
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    from statsmodels.tsa.ar_model import AR, ARResults
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.seasonal import  seasonal_decompose
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tsa.statespace.tools import diff
    from statsmodels.tsa.stattools import acovf, acf, pacf,pacf_yw,pacf_ols
    from statsmodels.tsa.stattools import adfuller
    #from skfuzzy import control as ctrl

#     %matplotlib inline

    # Import Library
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    from sklearn.metrics import davies_bouldin_score
    from sklearn.cluster import KMeans

    # Baca data dari file Excel
    df = pd.read_excel('/content/drive/MyDrive/Colab Notebooks/data_raw_2_tahun.xlsx')

    # Menampilkan contoh data
    #print(df.head())

    # Menampilkan kolom data
    #print(df.columns)

    # List semua kolom iops
    kolom_write_iops = df.filter(like='Sum of Datastore|Write IOPS').columns
    kolom_read_iops = df.filter(like='Sum of Datastore|Read IOPS').columns
    # List semua kolom disk
    kolom_disk_space = df.filter(like='Sum of Disk Space|Provisioned Space for VM (GB)').columns
    kolom_disk_used = df.filter(like='disk used').columns

    # Menambahkan kolom-kolom baru dengan nilai rata-ratanya
    df['Rata-rata Write IOPS'] = df[kolom_write_iops].mean(axis=1)
    df['Rata-rata Read IOPS'] = df[kolom_read_iops].mean(axis=1)
    df['Rata-rata Disk Space'] = df[kolom_disk_space].mean(axis=1)
    df['Rata-rata Disk Used'] = df[kolom_disk_used].mean(axis=1)

    # Menghasilkan DataFrame baru hanya dengan kolom yang diinginkan
    data_unit_disk_space_iops = df[['Unit', 'Rata-rata Write IOPS', 'Rata-rata Read IOPS', 'Rata-rata Disk Space', 'Rata-rata Disk Used']]

    # Menampilkan beberapa baris pertama DataFrame baru
    #print(data_unit_disk_space_iops.head())

    ### Grouping Data By MEAN

    # Mengelompokkan data berdasarkan kolom 'Unit' dan menghitung rata-rata
    data_unit_disk_space_iops_grouped = data_unit_disk_space_iops.groupby('Unit').mean().reset_index()

    # Menampilkan hasil pengelompokkan
    print(data_unit_disk_space_iops_grouped)

    #######################################################

    # Menentukan jumlah kluster yang diinginkan dengan metode elbow
    max_clusters = 10
    inertia = []

    # Melakukan pengelompokkan menggunakan KMeans untuk setiap jumlah kluster
    for k in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(data_unit_disk_space_iops_grouped[['Rata-rata Write IOPS', 'Rata-rata Read IOPS']])
        inertia.append(kmeans.inertia_)

    # Plot nilai inersia untuk menemukan elbow
    plt.plot(range(1, max_clusters + 1), inertia, marker='o')
    plt.xlabel('Jumlah Kluster')
    plt.ylabel('Inersia')
    plt.title('Metode Elbow untuk Menentukan Jumlah Kluster Optimal')
    plt.show()

    ####################################################

    for optimal_clusters in range(2, max_clusters + 1):
        # Memilih kolom-kolom yang akan digunakan untuk analisis KMeans
        features_kmeans = ['Rata-rata Disk Space', 'Rata-rata Disk Used']
        data_kmeans = data_unit_disk_space_iops_grouped[features_kmeans]

        # Melakukan pengelompokkan menggunakan KMeans
        kmeans = KMeans(n_clusters=optimal_clusters)
        kmeans.fit(data_kmeans)

        # Menambahkan kolom klaster ke DataFrame
        data_unit_disk_space_iops_grouped['klaster'] = kmeans.labels_

        # Mengambil nilai centroid
        centroids = kmeans.cluster_centers_

        # Visualisasi hasil pengelompokkan berdasarkan klaster baru
        plt.scatter(data_unit_disk_space_iops_grouped['Rata-rata Disk Space'], data_unit_disk_space_iops_grouped['Rata-rata Disk Used'], c=data_unit_disk_space_iops_grouped['klaster'], cmap='viridis', label='Data Points')
        plt.scatter(centroids[:, 0], centroids[:, 1], marker='x', color='red', label='Centroids')
        plt.xlabel('Rata-rata Disk Space')
        plt.ylabel('Rata-rata Disk Used')
        plt.colorbar(label='Klaster')
        plt.legend()
        plt.title(f'Visualisasi Rata-rata Disk Space dan Rata-rata Disk Used dengan KMeans Centroids (Kluster = {optimal_clusters})')
        plt.show()

        # Menyimpan hasil klaster ke file CSV dengan nama yang mencakup jumlah kluster optimal
        output_file_name = f'/content/drive/MyDrive/Colab Notebooks/hasil_klaster_disk_space_{optimal_clusters}.csv'
        data_unit_disk_space_iops_grouped.to_csv(output_file_name, index=False)

        # Menghitung Davies Bouldin Score
        dbi_score = davies_bouldin_score(data_kmeans, data_unit_disk_space_iops_grouped['klaster'])
        print(f'Davies Bouldin Score untuk {optimal_clusters} kluster:', dbi_score)


    ############################################################

    for optimal_clusters in range(2, max_clusters + 1):
        # Memilih kolom-kolom yang akan digunakan untuk analisis KMeans
        features_kmeans = ['Rata-rata Write IOPS', 'Rata-rata Read IOPS']
        data_kmeans = data_unit_disk_space_iops_grouped[features_kmeans]

        # Melakukan pengelompokkan menggunakan KMeans
        kmeans = KMeans(n_clusters=optimal_clusters)
        kmeans.fit(data_kmeans)

        # Menambahkan kolom klaster ke DataFrame
        data_unit_disk_space_iops_grouped['klaster'] = kmeans.labels_

        # Mengambil nilai centroid
        centroids = kmeans.cluster_centers_

        # Visualisasi hasil pengelompokkan berdasarkan klaster baru
        plt.scatter(data_unit_disk_space_iops_grouped['Rata-rata Write IOPS'], data_unit_disk_space_iops_grouped['Rata-rata Read IOPS'], c=data_unit_disk_space_iops_grouped['klaster'], cmap='viridis', label='Data Points')
        plt.scatter(centroids[:, 0], centroids[:, 1], marker='x', color='red', label='Centroids')
        plt.xlabel('Rata-rata Write IOPS')
        plt.ylabel('Rata-rata Read IOPS')
        plt.colorbar(label='Klaster')
        plt.legend()
        plt.title(f'Visualisasi Rata-rata Write IOPS dan Rata-rata Read IOPS dengan KMeans Centroids (Kluster = {optimal_clusters})')
        plt.show()

        # Menyimpan hasil klaster ke file CSV dengan nama yang mencakup jumlah kluster optimal
        output_file_name = f'/content/drive/MyDrive/Colab Notebooks/hasil_klaster_disk_space_iops_{optimal_clusters}.csv'
        data_unit_disk_space_iops_grouped.to_csv(output_file_name, index=False)

        # Menghitung Davies Bouldin Score
        dbi_score = davies_bouldin_score(data_kmeans, data_unit_disk_space_iops_grouped['klaster'])
        print(f'Davies Bouldin Score untuk {optimal_clusters} kluster:', dbi_score)


    ##############################################################

    ## Grouping per Unit

    # Baca data dari file Excel
    df = pd.read_excel('/content/drive/MyDrive/Colab Notebooks/data_raw_2_tahun.xlsx')

    # Hapus spasi ekstra dari nama kolom
    df.columns = df.columns.str.strip()

    # Hapus kolom 'Nomor', 'Nama Aplikasi', 'URL', dan 'Hostname'
    df = df.drop(['Nomor', 'Nama Aplikasi', 'URL', 'Hostname'], axis=1)

    # Hapus kolom yang memiliki awalan 'Sum of Datastore|Write IOPS' atau 'Sum of Datastore|Read IOPS'
    df = df.drop(df.filter(like='Sum of Datastore|Write IOPS').columns, axis=1)
    df = df.drop(df.filter(like='Sum of Datastore|Read IOPS').columns, axis=1)

    # Ganti nama kolom dengan awalan 'Sum of Disk Space|Provisioned Space for VM (GB)'
    df = df.rename(columns=lambda x: 'Total Disk Space' if 'Sum of Disk Space|Provisioned Space for VM (GB)' in x else x)

    # Ganti nama kolom dengan awalan 'disk used'
    df = df.rename(columns=lambda x: 'Total Disk Used' if 'disk used' in x else x)

    # Mengelompokkan berdasarkan 'Unit' tanpa melakukan agregasi
    grouped_df = df.groupby('Unit').sum().reset_index()

    # Menampilkan beberapa baris pertama DataFrame setelah mengelompokkan
    #print(grouped_df.head())

    # Menyimpan DataFrame ke dalam file CSV
    grouped_df.to_csv('/content/drive/MyDrive/Colab Notebooks/grouped_data.csv', index=False)

    ## Membuat FIle CSV Unit Loop Untuk Total Disk Used & Prediction

    import pandas as pd
    import matplotlib.pyplot as plt
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from sklearn.metrics import mean_squared_error

    # List untuk menyimpan hasil RMSE dan Mean
    rmse_results = []
    mean_results = []

    # DataFrame untuk menyimpan hasil RMSE tiap unit
    rmse_df = pd.DataFrame(columns=['Unit', 'RMSE'])

    # Loop untuk setiap Unit
    for idx, unit_name in enumerate(grouped_df['Unit']):
        # Mengambil data kolom ganjil untuk baris pertama mulai dari kolom ketiga
        odd_columns_data = grouped_df.iloc[idx, 2::2]  # Mulai dari indeks 2 (kolom ketiga), langkah 2

        # Menyimpan data ke dalam file dengan nama Unit
        file_name = f'/content/drive/MyDrive/Colab Notebooks/Disk Used {unit_name}.csv'
        odd_columns_data.to_csv(file_name, index=False)

        # Membaca kembali file CSV
        df_revised = pd.read_csv(file_name)

        # Mengganti nama kolom pertama dengan 'Total Disk Used'
        df_revised.columns.values[0] = 'Total Disk Used'

        # Menyimpan kembali file CSV dengan nama kolom yang sudah diganti
        df_revised.to_csv(file_name, index=False)

        # Baca data dari file CSV yang telah direvisi
        df_revised = pd.read_csv(file_name)

        # Tambahkan kolom baru dengan nilai yang sesuai
        df_revised['Date'] = pd.date_range(start='20220101', periods=len(df_revised), freq='MS').strftime('%Y%m%d')

        # Pindahkan kolom 'Date' ke sebelah kiri
        df_revised = df_revised[['Date'] + [col for col in df_revised if col != 'Date']]

        # Menyimpan DataFrame kembali ke dalam file CSV
        df_revised.to_csv(file_name, index=False)

        # Pesan selesai setelah loop selesai
        print(f"Selesai {unit_name}")

        # Membaca kembali file CSV
        df_revised = pd.read_csv(file_name, index_col='Date', parse_dates=True, skiprows=0)

        # Menggunakan values untuk mendapatkan array satu dimensi
        train = df_revised.iloc[0:13]
        test = df_revised.iloc[12:]

        fitted_model = ExponentialSmoothing(train['Total Disk Used'].values, trend='add', seasonal='add', seasonal_periods=6).fit()

        test_predictions_hw = fitted_model.forecast(steps=12)

        # Membuat DataFrame Pandas dari array NumPy
        predictions_df = pd.DataFrame({
            'Date': pd.date_range(start='2023-01-01', periods=12, freq='MS'),
            'Predictions': test_predictions_hw
        })

        # Hitung RMSE
        error_hw = mean_squared_error(test['Total Disk Used'], test_predictions_hw, squared=False)
        rmse_results.append(error_hw)

        # Hitung Mean
        mean_value = test['Total Disk Used'].mean()
        mean_results.append(mean_value)
        print(f"Hasil RMSE untuk {unit_name}: {error_hw}")
        print(f"Mean untuk {unit_name}: {mean_value}")

        # Menambahkan hasil RMSE ke DataFrame
        rmse_df = rmse_df.append({'Unit': unit_name, 'RMSE': error_hw}, ignore_index=True)

        # Plotting train, test, dan predictions
        plt.figure(figsize=(14, 8))
        plt.plot(train.index, train['Total Disk Used'], label='Train')
        plt.plot(test.index, test['Total Disk Used'], label='Test')
        plt.plot(predictions_df['Date'], predictions_df['Predictions'], label='Predictions')
        plt.xlabel('Date')
        plt.ylabel('Total Disk Used')
        plt.legend()
        plt.title(f'Holt-Winters Forecast for {unit_name}')

        # Menyimpan plot ke file gambar
        plt.savefig(f'/content/drive/MyDrive/Colab Notebooks/Predictions_Plot_{unit_name}.png')
        plt.close()

        # Menyimpan hasil prediksi ke dalam file CSV
        predictions_df.to_csv(f'/content/drive/MyDrive/Colab Notebooks/Predictions_{unit_name}.csv', index=False)

    # Menyimpan hasil RMSE tiap unit ke dalam satu file CSV
    rmse_csv_file = '/content/drive/MyDrive/Colab Notebooks/Holt_RMSE_results.csv'
    rmse_df.to_csv(rmse_csv_file, index=False)
    print(f'Hasil RMSE tiap unit disimpan di: {rmse_csv_file}')


    ###################################################################

    # Membaca kembali file CSV untuk setiap unit
    unit_dfs = []
    for unit_name in grouped_df['Unit']:
        file_name = f'/content/drive/MyDrive/Colab Notebooks/Disk Used {unit_name}.csv'
        unit_df = pd.read_csv(file_name, index_col='Date', parse_dates=True)
        unit_dfs.append(unit_df)

    # Gabungkan data dari semua unit
    total_df = pd.concat(unit_dfs, axis=1).sum(axis=1).to_frame(name='Total Disk Used')

    #print(total_df)

    ## Membagi Data menjadi Training dan Testing

    # Menentukan indeks untuk pemisahan data training dan testing
    split_index = int(len(total_df) * 0.5)  # Misalnya, menggunakan 80% data untuk training

    # Memisahkan data menjadi training dan testing
    train_total = total_df.iloc[:split_index]
    test_total = total_df.iloc[split_index:]

    ## Membuat Model dan Melakukan Prediksi pada Data Training

    # Membuat model dan melakukan prediksi pada data training
    final_model = ExponentialSmoothing(train_total['Total Disk Used'].values, trend='add', seasonal='add', seasonal_periods=6).fit()
    train_predictions = final_model.fittedvalues

    ## Melakukan Prediksi pada Data Testing

    # Melakukan prediksi pada data testing
    test_predictions = final_model.forecast(steps=len(test_total))

    ## Menyimpan Hasil Prediksi Data Training dan Testing

    # Membuat DataFrame Pandas dari array NumPy untuk data training
    train_predictions_df = pd.DataFrame({
        'Date': train_total.index,
        'Predictions': train_predictions
    })

    # Menyimpan hasil prediksi data training ke dalam file CSV
    train_predictions_df.to_csv('/content/drive/MyDrive/Colab Notebooks/Train_Predictions_Total_Unit.csv', index=False)

    # Membuat DataFrame Pandas dari array NumPy untuk data testing
    test_predictions_df = pd.DataFrame({
        'Date': test_total.index,
        'Predictions': test_predictions
    })

    # Menyimpan hasil prediksi data testing ke dalam file CSV
    test_predictions_df.to_csv('/content/drive/MyDrive/Colab Notebooks/Test_Predictions_Total_Unit.csv', index=False)

    ## Menampilkan Plot Data Training dan Testing

    # Plotting data training dan testing
    plt.figure(figsize=(14, 8))
    plt.plot(train_total.index, train_total['Total Disk Used'], label='Train')
    plt.plot(test_total.index, test_total['Total Disk Used'], label='Test')
    plt.plot(train_predictions_df['Date'], train_predictions_df['Predictions'], label='Train Predictions')
    plt.plot(test_predictions_df['Date'], test_predictions_df['Predictions'], label='Test Predictions')
    plt.xlabel('Date')
    plt.ylabel('Total Disk Used')
    plt.legend()
    plt.title('Holt-Winters Forecast for Total Unit')
    plt.show()

    ## Membuat Model Dan Prediksi

    # Membuat model dan melakukan prediksi
    final_model = ExponentialSmoothing(total_df['Total Disk Used'].values, trend='add', seasonal='add', seasonal_periods=6).fit()
    forecast_predictions = final_model.forecast(steps=12)

    # Menghitung RMSE
    rmse_total = np.sqrt(mean_squared_error(test_total['Total Disk Used'], forecast_predictions))
    print(f"Hasil RMSE untuk Total Unit: {rmse_total}")

    # Menambahkan perhitungan mean
    mean_total = total_df['Total Disk Used'].mean()
    print(f"Mean dari Total Disk Used: {mean_total}")

    ## Menyimpan hasil prediksi total unit ke dalam DataFrame dan file CSV

    # Membuat DataFrame Pandas dari array NumPy
    forecast_df_total = pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=12, freq='MS'),
        'Predictions': forecast_predictions
    })

    # Menyimpan hasil prediksi total unit ke dalam file CSV
    forecast_df_total.to_csv('/content/drive/MyDrive/Colab Notebooks/Predictions_Total_Unit.csv', index=False)

    ## Plot Prediksi

    # Plotting total unit
    plt.figure(figsize=(14, 8))
    total_df.plot(legend=True, label='Actual', figsize=(14, 8))
    forecast_df_total.set_index('Date')['Predictions'].plot(legend=True, label='Holt Winters Forecast 1 year')
    plt.xlabel('Date')
    plt.ylabel('Total Disk Used')
    plt.title('Holt-Winters Forecast for Total Unit')
    plt.savefig('/content/drive/MyDrive/Colab Notebooks/Predictions_Plot_Total_Unit.png')
    plt.show()

    #############################################################

    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error
    import matplotlib.pyplot as plt

    # List untuk menyimpan hasil prediksi, RMSE, dan rumus regresi
    results_list = []

    # DataFrame untuk menyimpan hasil RMSE tiap unit
    rmse_df = pd.DataFrame(columns=['Unit', 'Regresi RMSE'])

    # Loop untuk setiap Unit
    for idx, unit_name in enumerate(grouped_df['Unit']):
        # Membaca data dari file CSV
        file_name = f'/content/drive/MyDrive/Colab Notebooks/Disk Used {unit_name}.csv'
        df = pd.read_csv(file_name)

        # Tambahkan kolom 'Month' sebagai variabel independen (X)
        df['Month'] = range(1, len(df) + 1)

        # Pisahkan variabel independen (X) dan variabel dependen (y)
        X = df[['Month']]
        y = df['Total Disk Used']

        # Inisialisasi model regresi linear
        model = LinearRegression()

        # Melatih model menggunakan data
        model.fit(X, y)

        # Membuat DataFrame untuk prediksi 12 bulan ke depan
        next_months = pd.DataFrame({'Month': range(len(df) + 1, len(df) + 13)})
        predictions = model.predict(next_months)

        # Menambahkan hasil prediksi ke DataFrame
        next_months['Total Disk Used Prediction'] = predictions

        # Hitung RMSE
        rmse_value = mean_squared_error(y, model.predict(X), squared=False)

        # Menyimpan hasil RMSE ke DataFrame
        rmse_df = rmse_df.append({'Unit': unit_name, 'Regresi RMSE': rmse_value}, ignore_index=True)

        # Simpan hasil prediksi, RMSE, dan rumus regresi ke dalam list
        results_list.append({
            'unit_name': unit_name,
            'predictions': predictions,
            'rmse': rmse_value,
            'regression_formula': f'y = {model.coef_[0]:.2f} * x + {model.intercept_:.2f}'
        })

        # Plotting data dan regresi linear
        plt.scatter(df['Month'], y, label='Actual Data')
        plt.plot(df['Month'], model.predict(X), color='red', label='Linear Regression')
        plt.scatter(next_months['Month'], predictions, color='green', marker='x', label='Predictions for Next 12 Months')
        plt.xlabel('Month')
        plt.ylabel('Total Disk Used')
        plt.legend()
        plt.title(f'Linear Regression for {unit_name}')
        plt.show()

        # Simpan DataFrame yang berisi prediksi ke CSV
        predictions_csv_file = f'/content/drive/MyDrive/Colab Notebooks/Predictions Regresi {unit_name}.csv'
        next_months.to_csv(predictions_csv_file, index=False)

    # Menyimpan hasil RMSE tiap unit ke dalam satu file CSV
    rmse_csv_file = '/content/drive/MyDrive/Colab Notebooks/RMSE_Results_Regresi.csv'
    rmse_df.to_csv(rmse_csv_file, index=False)
    print(f'Hasil RMSE tiap unit disimpan di: {rmse_csv_file}')

    # Menampilkan hasil prediksi, RMSE, dan rumus regresi untuk setiap unit
    for result in results_list:
        print(f'Prediksi Total Disk Used untuk {result["unit_name"]}: {result["predictions"]}')
        print(f'RMSE untuk {result["unit_name"]}: {result["rmse"]}')
        print(f'Rumus Regresi untuk {result["unit_name"]}: {result["regression_formula"]}')


    #############################################################

    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error
    import matplotlib.pyplot as plt

    # Tambahkan kolom 'Month' sebagai variabel independen (X)
    total_df['Month'] = range(1, len(total_df) + 1)

    # Pisahkan variabel independen (X) dan variabel dependen (y)
    X = total_df[['Month']]
    y = total_df['Total Disk Used']

    # Inisialisasi model regresi linear
    model = LinearRegression()

    # Melatih model menggunakan data
    model.fit(X, y)

    # Membuat DataFrame untuk prediksi 12 bulan ke depan
    next_months = pd.DataFrame({'Month': range(len(total_df) + 1, len(total_df) + 13)})

    # Menggunakan indeks dari bulan terakhir pada total_df
    last_month = total_df.index.max()
    next_months.index = pd.date_range(start=last_month + pd.DateOffset(months=1), periods=12, freq='MS')

    # Melakukan prediksi
    next_months['Total Disk Used Prediction'] = model.predict(next_months[['Month']])

    # Hitung RMSE
    rmse_value = mean_squared_error(y, model.predict(X), squared=False)

    # Simpan hasil RMSE ke DataFrame
    rmse_df = pd.DataFrame({'Unit': ['Total'], 'Regresi RMSE': [rmse_value]})

    # Plotting data dan regresi linear
    plt.scatter(total_df.index, y, label='Actual Data')
    plt.plot(total_df.index, model.predict(X), color='red', label='Linear Regression')
    plt.scatter(next_months.index, next_months['Total Disk Used Prediction'], color='green', marker='x', label='Predictions for Next 12 Months')
    plt.xlabel('Date')
    plt.ylabel('Total Disk Used')
    plt.legend()
    plt.title('Linear Regression for Total Data')
    plt.show()

    # Menampilkan hasil prediksi, RMSE, dan rumus regresi
    print(f'Prediksi Total Disk Used:\n{next_months}')
    print(f'RMSE untuk Total Data: {rmse_value}')
    print(f'Rumus Regresi untuk Total Data: y = {model.coef_[0]:.2f} * x + {model.intercept_:.2f}')

    # Menyimpan hasil RMSE ke dalam satu file CSV
    rmse_csv_file = '/content/drive/MyDrive/Colab Notebooks/RMSE_Results_Total_Regresi.csv'
    rmse_df.to_csv(rmse_csv_file, index=False)
    print(f'Hasil RMSE disimpan di: {rmse_csv_file}')

    # Simpan hasil prediksi ke dalam file CSV
    predictions_csv_file = '/content/drive/MyDrive/Colab Notebooks/Predictions_Regresi_Total.csv'
    next_months.to_csv(predictions_csv_file, index=False)
    print(f'Hasil prediksi disimpan di: {predictions_csv_file}')


        # Add content for unit analysis

    elif selected_page == "Total Analysis":
        st.header("Total Analysis")

        # Add content for total analysis

if __name__ == "__main__":
    main()