### Building a Streaming Analytics Pipeline on Azure PostgreSQL

A near-real-time stock market analytics platform that tracks approximately 300 US stocks using one-minute price bars from Yahoo Finance. The system ingests market data through an Azure Function, stores it in Azure Database for PostgreSQL, detects anomalous price and volume movements, and updates an online machine learning model.

The interactive Streamlit dashboard refreshes every 15 seconds, providing market indicators, stock comparisons, candlestick charts, market breadth, anomaly reports, and machine learning performance metrics.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Project Objectives](#project-objectives)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Key Features](#key-features)
- [Dashboard Components](#dashboard-components)
- [Database Design](#database-design)
- [Data Ingestion Pipeline](#data-ingestion-pipeline)
- [Outlier Detection](#outlier-detection)
- [Online Machine Learning](#online-machine-learning)
- [Installation and Setup](#installation-and-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Dashboard](#running-the-dashboard)
- [Azure Deployment](#azure-deployment)
- [Performance and Evaluation](#performance-and-evaluation)
- [Limitations](#limitations)
- [Team Members](#team-members)

---

## Project Overview

This project implements an end-to-end streaming analytics pipeline for monitoring the US stock market.

Market data is collected from Yahoo Finance in one-minute intervals and ingested into Azure Database for PostgreSQL by an Azure Function. The database maintains stock information, historical price bars, ingestion logs, detected outliers, machine learning predictions, and model evaluation metrics.

A Streamlit dashboard connects directly to PostgreSQL and periodically refreshes its visualizations and indicators to reflect newly ingested records.

The system combines three essential components:

1. **Live Dashboard:** Monitors stock prices, trading volumes, market trends, and ingestion activity.
2. **Outlier Detection:** Identifies unusual price movements and volume spikes using a robust statistical method.
3. **Online Machine Learning:** Uses an incrementally trained logistic regression model to predict whether a stock's price will rise in the next minute.

The project demonstrates how continuously arriving data can be transformed into useful analytical insights through cloud database infrastructure, automated ingestion, statistical analysis, and machine learning.

> **Note:** The dashboard refreshes every 15 seconds, while the ingestion pipeline operates approximately once per minute. Dashboard refreshes therefore do not necessarily correspond to new market data.

---

## Project Objectives

The main objectives are to:

- Design and deploy a relational database on Azure Database for PostgreSQL.
- Collect one-minute price bars for approximately 300 US stocks.
- Simulate a continuous data stream through scheduled data collection and ingestion.
- Insert new observations into PostgreSQL and maintain ingestion logs.
- Build a live dashboard displaying key market indicators.
- Compare the performance of two selected stocks over configurable time windows.
- Detect anomalous price movements and trading-volume spikes.
- Develop an online machine learning model that updates as new observations arrive.
- Evaluate model performance using accuracy, F1 score, baseline accuracy, precision, recall, and a confusion matrix.
- Demonstrate an end-to-end cloud analytics pipeline.

---

## System Architecture

The application consists of four main layers.

### 1. Data Source

Yahoo Finance supplies market data for the selected stock universe.

The pipeline works with one-minute OHLCV bars:

- **Open:** First recorded price for the minute.
- **High:** Highest recorded price during the minute.
- **Low:** Lowest recorded price during the minute.
- **Close:** Last recorded price for the minute.
- **Volume:** Number of shares traded during the minute.

### 2. Ingestion Layer

An Azure Function runs on a scheduled basis, retrieves the latest market observations, and inserts new records into PostgreSQL.

The pipeline also records ingestion activity, including the execution time and number of price bars inserted.

### 3. Storage and Analytics Layer

Azure Database for PostgreSQL stores the relational data used by the dashboard and analytical components.

The analytics pipeline includes:

- Robust statistical outlier detection.
- Incremental logistic regression.
- Prediction records and actual outcomes.
- Model evaluation metrics.
- SQL-based market statistics and aggregations.

### 4. Visualization Layer

A Streamlit application queries PostgreSQL and displays market data through interactive Plotly charts and metric cards.

The dashboard uses Streamlit fragments configured to refresh every 15 seconds.

### Architecture Diagram

```text
                Yahoo Finance
                      |
                      v
          +------------------------+
          |    Azure Function      |
          |                        |
          | Fetch Latest OHLCV Data|
          | Validate / Transform   |
          | Insert New Price Bars  |
          +-----------+------------+
                      |
                      v
          +------------------------+
          | Azure PostgreSQL       |
          |                        |
          | stocks                 |
          | price_bars             |
          | ingestion_runs         |
          | outliers               |
          | predictions            |
          | model_metrics          |
          +-----------+------------+
                      |
             +--------+--------+
             |                 |
             v                 v
 +----------------------+  +----------------------+
 | Outlier Detection    |  | Online ML Pipeline   |
 |                      |  |                      |
 | Robust Z-Score       |  | Logistic Regression  |
 | Price Jumps          |  | Incremental Training |
 | Volume Spikes        |  | Predictions / Metrics|
 +----------+-----------+  +----------+-----------+
            |                         |
            +------------+------------+
                         |
                         v
              +----------------------+
              | Streamlit Dashboard  |
              |                      |
              | Market KPIs          |
              | Stock Comparisons    |
              | Candlestick Charts   |
              | Market Heatmap       |
              | Outlier Reports      |
              | ML Evaluation        |
              +----------------------+
```

**Note:** The ingestion, outlier detection, and machine learning processes should be deployed or scheduled according to their respective implementations. The Streamlit dashboard reads their results from PostgreSQL; it does not itself execute the ingestion or model-training pipeline.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application and analytics development |
| Azure Functions | Scheduled market-data ingestion |
| Azure Database for PostgreSQL | Relational database and persistent storage |
| PostgreSQL | SQL queries, joins, aggregations, and analytics |
| Yahoo Finance | Market-data source |
| Streamlit | Interactive web dashboard |
| Pandas | DataFrame processing and transformations |
| Plotly Express | Interactive statistical charts |
| Plotly Graph Objects | Custom charts, candlesticks, and heatmaps |
| psycopg2 | PostgreSQL database connectivity |
| python-dotenv | Local environment-variable configuration |
| Scikit-learn-compatible online learning approach | Incremental logistic regression, depending on the worker implementation |
| Git and GitHub | Version control and project collaboration |

The dashboard imports Pandas, Plotly, psycopg2, Streamlit, and Python's standard libraries.

The ingestion and analytics workers may require additional dependencies that should be documented in their respective deployment configurations.

---

## Key Features

### Live Market Monitoring

The dashboard provides an overview of the monitored stock universe, stored price bars, recent ingestion activity, detected outliers, and machine learning accuracy.

### Stock Comparison

Users can select two stocks and compare their performance using several metrics and configurable time windows.

### Technical Market Visualization

Interactive charts provide price trends, candlestick patterns, volume information, market breadth, and stock performance rankings.

### Statistical Anomaly Detection

The outlier dashboard displays unusual price movements and volume spikes, along with detection scores and explanations.

### Online Machine Learning

The machine learning dashboard tracks predictive performance and displays accuracy, F1 score, baseline accuracy, and confusion-matrix statistics.

### Cloud Database Integration

The dashboard retrieves its data directly from Azure PostgreSQL using environment-based database configuration and SSL connections.

---

## Dashboard Components

The dashboard is divided into seven main analytical sections.

### 1. Market Status and KPIs

The overview section provides six key indicators.

| Indicator | Description |
|---|---|
| Stocks Tracked | Number of stock symbols in the database |
| Price Bars Stored | Total number of stored price observations |
| Records per Minute | Average number of inserted price bars per minute over the last five minutes |
| Outliers Flagged | Total number of recorded outliers |
| Model Accuracy | Most recently recorded model accuracy |
| Last Pipeline Run | Timestamp of the latest ingestion run, displayed in UTC |

The dashboard also displays a market-session indicator based on Eastern Time.

Supported session labels include:

- Pre-market: 4:00 AM–9:30 AM ET.
- Regular trading: 9:30 AM–4:00 PM ET.
- After-hours trading: 4:00 PM–8:00 PM ET.
- Market closed: Weekends and times outside the configured sessions.

A separate data-freshness indicator checks whether the latest stored price bar is less than ten minutes old.

**Note:** The market-status logic uses weekdays and clock times rather than an exchange calendar. It does not account for US market holidays or early closing sessions.

### 2. Stock Comparison

Users can choose two stock symbols and compare their market performance.

Available time windows:

- Last 30 minutes.
- Last 60 minutes.
- Last 2 hours.
- Latest full day.
- All available data.

Available metrics:

- Price.
- Percentage change.
- Volume.
- Ten-minute rolling volatility.

The comparison charts display the selected metric for each stock.

The dashboard also calculates:

- Percentage change across the selected window.
- Highest observed price.
- Lowest observed price.
- Total recorded trading volume.
- Correlation between aligned one-minute returns, when sufficient overlapping observations exist.

Detected price outliers can be overlaid on the price chart.

### 3. Candlestick Charts

The candlestick section displays one-minute OHLC price bars for the two selected stocks.

Each candle represents:

- Opening price.
- Highest price.
- Lowest price.
- Closing price.

Green candles indicate that the closing price exceeded the opening price. Red candles indicate that the closing price was below the opening price.

These charts help visualize short-term price movements and potential volatility.

### 4. Market Leaders

The market-leaders section ranks stocks according to their performance during the selected time window.

**Top Gainers**

The ten stocks with the highest percentage price increases.

**Top Losers**

The ten stocks with the largest percentage price decreases.

**Most Traded Stocks**

The ten stocks with the highest total recorded trading volume.

**Most Volatile Stocks**

The ten stocks with the largest standard deviation of one-minute returns.

These rankings provide a quick overview of market activity and help identify stocks experiencing significant movements.

### 5. Market Heatmap

The heatmap provides a visual summary of the monitored stock universe.

Each tile represents a stock.

- Tile size corresponds to recorded trading volume.
- Tile color represents percentage price change.
- Green indicates positive performance.
- Red indicates negative performance.
- Neutral colors represent movements near zero.

Hovering over a tile reveals the stock symbol, percentage change, and recorded trading volume.

### 6. Market Breadth and Ingestion Activity

This section contains two charts.

**Market Breadth**

Displays the percentage of stocks whose closing price increased compared with their preceding recorded bar.

A value above 50% indicates that more stocks rose than fell among the eligible observations.

**Ingestion Activity**

Displays the number of new price bars recorded by recent ingestion runs.

This helps monitor ingestion volume and identify changes in pipeline activity.

### 7. Outlier Detection and Machine Learning

The final sections display detected anomalies and machine learning evaluation results.

The outlier section provides recent anomaly records and rankings of stocks with the most detected price jumps and volume spikes.

The machine learning section displays evaluation metrics and a confusion matrix for predictions of next-minute price direction.

---

## Database Design

The PostgreSQL database contains six logical tables referenced by the dashboard.

The actual column definitions, data types, indexes, constraints, and foreign keys should be documented alongside the database initialization scripts.

### 1. `stocks`

Stores the stock symbols tracked by the application.

The dashboard uses this table to populate the stock-selection dropdowns.

The `stock_id` column identifies a stock, while `symbol` stores its market ticker.

Example symbols include AAPL and MSFT.

### 2. `price_bars`

Stores one-minute stock price observations.

| Column | Purpose |
|---|---|
| `bar_id` | Unique identifier for a price bar |
| `stock_id` | Reference to the corresponding stock |
| `bar_time` | Timestamp associated with the price bar |
| `open` | Opening price |
| `high` | Highest price |
| `low` | Lowest price |
| `close` | Closing price |
| `volume` | Number of shares traded |

The dashboard joins this table with `stocks` to retrieve market data by ticker.

### 3. `ingestion_runs`

Stores ingestion execution history.

| Column | Purpose |
|---|---|
| `run_at` | Timestamp of an ingestion run |
| `bars_inserted` | Number of price bars inserted during the run |

These records support ingestion monitoring and recent throughput calculations.

### 4. `outliers`

Stores detected anomalies.

| Column | Purpose |
|---|---|
| `bar_id` | Reference to the associated price bar |
| `score` | Anomaly score |
| `reason` | Human-readable explanation |
| `method` | Detection method |
| `detected_at` | Timestamp when the anomaly was detected |

The dashboard uses these records to identify unusual price movements and trading-volume spikes.

### 5. `predictions`

Stores machine learning predictions and their observed outcomes.

| Column | Purpose |
|---|---|
| `predicted_up` | Whether the model predicted an upward movement |
| `actual_up` | Whether the observed outcome was an upward movement |

These fields support confusion-matrix calculations and classification metrics.

Additional columns may be present to identify the stock, associated bar, prediction time, or model version.

### 6. `model_metrics`

Stores model evaluation results over time.

| Column | Purpose |
|---|---|
| `recorded_at` | Timestamp when the metrics were recorded |
| `accuracy` | Fraction of correct predictions |
| `f1` | F1 score |
| `baseline_accuracy` | Accuracy of a baseline predictor |

The dashboard uses this table to display model performance over time.

### Relationships

The principal database relationships are:

```text
stocks
  |
  | stock_id
  v
price_bars
  |
  +------------------+
  |                  |
  | bar_id           | bar_id
  v                  v
outliers          predictions

ingestion_runs
    |
    +-- Records ingestion execution history

model_metrics
    |
    +-- Records model evaluation results
```

The `stocks` and `price_bars` relationship is used extensively throughout the dashboard.

The `outliers` table references `price_bars` through `bar_id`.

The exact relationship between `predictions` and the stock or price-bar tables depends on the database schema implemented by the team.

**Implementation note:** Verify that the database initialization scripts define the intended foreign keys and indexes. The diagram describes the logical data model and should not be interpreted as proof that every constraint is already deployed.

---

## Data Ingestion Pipeline

The ingestion pipeline simulates a continuous market-data stream by periodically retrieving and storing one-minute price bars.

### Pipeline Workflow

1. Execute the scheduled Azure Function.
2. Retrieve recent market observations for the configured stock universe.
3. Validate and transform the incoming records.
4. Associate each observation with the correct stock identifier.
5. Insert new price bars into PostgreSQL.
6. Record the ingestion execution and number of inserted bars.
7. Make the new records available to downstream analytics and the dashboard.

### Ingestion Frequency

The intended ingestion schedule is approximately once per minute.

For a universe of approximately 300 stocks, one complete observation per stock per minute would produce approximately:

- 300 price bars per minute.
- 18,000 price bars per hour.
- 432,000 price bars per day over 24 hours.

These figures are theoretical estimates assuming every stock produces one new bar every minute. Actual ingestion volume depends on market hours, data availability, missing observations, duplicate handling, and pipeline execution.

The dashboard reports the actual number of inserted bars using the `ingestion_runs` table.

### Data Integrity Considerations

A production-quality ingestion pipeline should implement:

- Duplicate detection.
- Idempotent inserts or upserts.
- Input validation.
- Retry handling for transient failures.
- Database connection management.
- Logging and error reporting.
- Appropriate timestamp handling.
- Unique constraints for stock and bar-time combinations, where applicable.

These measures help maintain consistent data when scheduled functions retry or encounter interruptions.

---

## Outlier Detection

The application includes a statistical anomaly detection system designed to identify unusual price changes and trading-volume spikes.

### Detection Method

The dashboard describes the method as a **robust z-score based on the median and median absolute deviation (MAD)**.

Unlike a conventional z-score based on the mean and standard deviation, this approach uses robust statistics that are less sensitive to extreme observations.

For a sequence of observations \(x\), the median absolute deviation is:

\[
MAD = \operatorname{median}(|x_i - \operatorname{median}(x)|)
\]

A common robust z-score definition is:

\[
z_i = \frac{0.6745(x_i - \operatorname{median}(x))}{MAD}
\]

When the MAD is nonzero, observations with sufficiently large absolute robust z-scores can be flagged as potential anomalies.

The dashboard describes a threshold of:

\[
|z_i| > 3.5
\]

The intended detection categories are:

- **Price jumps:** Unusually large one-minute price movements.
- **Volume spikes:** Unusually high or low trading volume relative to recent observations.

The dashboard references the following method identifiers:

- `price_jump_robust_z`
- `volume_spike_robust_z`

### Detection Window

The dashboard describes the detector as operating over approximately the last 90 minutes of observations per stock.

It also notes that sufficient history is needed before anomaly detection becomes useful.

### Dashboard Output

The outlier section provides:

- Stock symbol.
- Bar timestamp.
- Anomaly score.
- Detection reason.
- Detection method.
- A ranking of stocks with the most flagged anomalies.

The overview also highlights recent outliers detected during the preceding five minutes.

### Interpretation

An anomaly is not necessarily an error or a trading opportunity.

Large price movements and volume spikes can occur naturally in financial markets. The detector identifies statistically unusual observations for further investigation rather than establishing that an observation is incorrect.

**Implementation note:** The Streamlit application consumes precomputed records from the `outliers` table. The robust z-score calculation must be implemented in the ingestion or analytics worker; it is not performed by the displayed Streamlit code itself.

---

## Online Machine Learning

The machine learning component predicts whether a stock's price will increase during the next minute.

The dashboard describes an incrementally trained logistic regression model using stochastic gradient descent (SGD).

### Prediction Objective

The model predicts a binary outcome:

\[
y_t =
\begin{cases}
1 & \text{if the next observed closing price is higher} \\
0 & \text{otherwise}
\end{cases}
\]

The exact target definition should be confirmed against the model-training implementation.

### Online Learning Workflow

The intended workflow is:

1. Receive a new price bar.
2. Construct the model features.
3. Generate a prediction before training on that observation's outcome.
4. Observe the realized outcome once the required future price data becomes available.
5. Evaluate the prediction.
6. Update the model incrementally using the newly labeled example.
7. Record the prediction and evaluation metrics in PostgreSQL.
8. Repeat as additional observations arrive.

This is known as **test-then-train** evaluation.

It helps reduce temporal leakage by ensuring that a prediction is generated before the model learns from the example being evaluated.

### Incremental Training

Traditional batch training usually requires retraining on a collected dataset.

Online learning updates the model incrementally as new labeled observations become available.

The dashboard describes an SGD logistic regression model updated through `partial_fit`.

This approach supports continuous adaptation without retraining the entire model from scratch after every observation.

### Model Evaluation

The dashboard tracks several evaluation metrics.

| Metric | Description |
|---|---|
| Accuracy | Fraction of predictions that are correct |
| F1 Score | Harmonic mean of precision and recall |
| Baseline Accuracy | Accuracy of a baseline prediction strategy |
| Precision | Fraction of predicted upward movements that were actually upward |
| Recall | Fraction of actual upward movements correctly identified |
| Confusion Matrix | Counts of correct and incorrect predictions |

The confusion matrix contains:

| | Predicted Up | Predicted Down |
|---|---:|---:|
| Actually Up | True Positive (TP) | False Negative (FN) |
| Actually Down | False Positive (FP) | True Negative (TN) |

Precision is calculated as:

\[
\text{Precision} = \frac{TP}{TP + FP}
\]

Recall is calculated as:

\[
\text{Recall} = \frac{TP}{TP + FN}
\]

The F1 score is:

\[
F1 = 2 \times \frac{\text{Precision} \times \text{Recall}}
{\text{Precision} + \text{Recall}}
\]

The implementation should handle cases where denominators are zero.

### Model Dashboard

The machine learning section displays:

- Accuracy over time.
- F1 score over time.
- Baseline accuracy over time.
- Confusion matrix.
- Total number of evaluated predictions.
- Precision and recall.

### Evaluation Considerations

Financial market prediction is difficult, and a model that performs well on historical data may not generalize to future observations.

Model evaluation should therefore consider:

- Chronological evaluation.
- Prevention of future-data leakage.
- Class imbalance.
- Comparison against a meaningful baseline.
- Performance across different market conditions.
- Stability as new observations arrive.

The model's displayed accuracy should not be interpreted as evidence of profitability or investment performance.

**Implementation note:** The Streamlit application visualizes the prediction and evaluation records stored in PostgreSQL. The online training logic runs in the separate model-processing component.

---

## Installation and Setup

### Prerequisites

Before running the dashboard, ensure you have:

- Python 3.10 or a compatible version supported by your dependencies.
- Access to an Azure Database for PostgreSQL instance.
- Network access from your computer to the database server.
- The required database schema and tables.
- Database credentials with permission to read the dashboard's tables.
- Git installed, if cloning the project repository.

### 1. Clone the Repository

```bash
git clone https://github.com/puneeth164/stock-market-dashboard
```

### 2. Create a Virtual Environment

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the packages required by the dashboard:

```bash
pip install -r requirements.txt
```

### 4. Configure the Database

Create a `.env` file in the project root for local development.

```dotenv
DATABASE_HOST=your-server.postgres.database.azure.com
DATABASE_NAME=your_database_name
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_PORT=5432
DATABASE_SSLMODE=require
```

Replace the example values with the credentials and connection details for your Azure PostgreSQL instance.


### 5. Verify Database Connectivity

Before starting the dashboard, verify that:

- The PostgreSQL server is running.
- The database exists.
- The configured user can authenticate.
- The server firewall allows connections from the dashboard host.
- SSL requirements are satisfied.
- The required tables and columns exist.

The application attempts to establish a database connection when it starts. If the connection fails, it displays an error and stops execution.

---

## Environment Configuration

The dashboard reads database settings from environment variables.

| Variable | Required | Description |
|---|---|---|
| `DATABASE_HOST` | Yes | PostgreSQL server hostname |
| `DATABASE_NAME` | Yes | Database name |
| `DATABASE_USER` | Yes | Database username |
| `DATABASE_PASSWORD` | Yes | Database password |
| `DATABASE_PORT` | No | Database port; defaults to `5432` |
| `DATABASE_SSLMODE` | No | PostgreSQL SSL mode; defaults to `require` |

For local development, the application attempts to load variables from `.env` using `python-dotenv`.

In Azure, configure these values through the application's environment settings rather than committing secrets to the repository.

The dashboard uses `psycopg2` for database connectivity and enables autocommit on its cached database connection.

It also attempts to clear and recreate the cached connection if a connection-related error occurs during a query.

### Security Recommendations

- Store production credentials in Azure application settings or an appropriate secrets manager.
- Restrict database firewall access to trusted networks.
- Use least-privilege database accounts.
- Avoid logging passwords or other sensitive connection details.
- Do not commit credentials, connection strings, or secret configuration files to Git.

---

## Running the Dashboard

Start the Streamlit application using:

```bash
streamlit run app.py
```

Streamlit will display a local URL, typically:

```text
http://localhost:8501
```

Open the URL in a web browser.

### Expected Behavior

When the application starts successfully, it will:

1. Connect to Azure PostgreSQL.
2. Retrieve available stock symbols.
3. Display the market-status indicator and KPI cards.
4. Populate the stock-selection controls.
5. Render price comparison charts and candlesticks.
6. Display market leaders and the market heatmap.
7. Show ingestion activity, detected outliers, and model evaluation metrics.

The dashboard's Streamlit fragments refresh every 15 seconds.

If no stock symbols are available, the dashboard prompts the user to start the ingestion pipeline and wait for data to arrive.

If the database connection fails, verify the environment variables, server status, credentials, SSL configuration, and firewall rules.

---

## Azure Deployment

The project uses Azure services to host its database and scheduled ingestion process.

### Azure PostgreSQL

The PostgreSQL instance stores market observations and analytical results.

Before deploying the dashboard, ensure that the required schema has been created and that the database contains the tables expected by the application.

### Azure Function

The ingestion function should be configured to execute approximately once per minute.

Its responsibilities include:

- Retrieving recent market data.
- Processing observations.
- Writing new price bars to PostgreSQL.
- Recording ingestion activity.
- Triggering or coordinating downstream analytics, where applicable.

The function's schedule, timeout, retry behavior, and database access must be configured according to the selected Azure Functions hosting plan.

### Dashboard Hosting

The Streamlit application can be deployed to a suitable Python hosting environment.

The hosting environment must have:

- The dashboard dependencies installed.
- The database environment variables configured.
- Network connectivity to Azure PostgreSQL.
- An appropriate startup command.
- Access to the required database tables.

For example, the startup command may be:

```bash
streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```

Use the port and startup configuration required by the chosen hosting service.


## Performance and Evaluation

The project should be evaluated across ingestion, storage, analytics, and visualization.

### Ingestion Performance

Measure:

- Price bars inserted per minute.
- Number of stocks processed per run.
- Successful versus failed ingestion runs.
- Duplicate observations prevented.
- Ingestion latency.
- Time since the latest successful run.

### Dashboard Performance

Measure:

- Dashboard startup time.
- SQL query execution time.
- Dashboard refresh behavior.
- Time between a database insert and its appearance on the dashboard.
- Performance as historical data volume increases.

### Outlier Detection Performance

Evaluate:

- Number of anomalies detected.
- Distribution of anomaly scores.
- Price jumps versus volume spikes.
- Frequency of repeated anomaly flags.
- False positives, where labeled examples are available.

### Machine Learning Performance

Evaluate:

- Accuracy.
- F1 score.
- Precision.
- Recall.
- Baseline accuracy.
- Prediction volume.
- Performance over time.

Compare the online model against a simple baseline, such as always predicting the majority class.

### Suggested Acceptance Criteria

| Requirement | Validation |
|---|---|
| Relational database | At least three related tables are deployed |
| Data ingestion | New market observations are inserted automatically |
| Streaming throughput | Measured insertion rate meets the project target |
| Dashboard | Displays database-backed indicators and charts |
| Near-real-time updates | New records appear after the next successful refresh |
| Outlier detection | Anomaly records are generated and displayed |
| Online machine learning | Predictions and evaluation metrics are updated over time |
| Cloud deployment | Database and scheduled ingestion run in Azure |
| Demonstration | Final report and five-minute presentation are completed |

Record actual measurements during testing rather than treating the intended configuration as proof of achieved performance.

---

## Limitations

The current design has several important limitations.

### Market Data Availability

Yahoo Finance data availability, historical depth, and update timing may vary. The pipeline depends on the source being accessible and returning usable observations.

### Market Session Accuracy

The dashboard calculates market status using weekdays and Eastern Time. It does not currently account for official US market holidays, early closes, or exceptional trading sessions.

### Dashboard Refresh

The dashboard refreshes every 15 seconds, but new market data is expected approximately once per minute. Refreshing the interface more frequently does not make the source data arrive more frequently.

### Data Freshness

The freshness indicator checks whether the most recent stored price bar is less than ten minutes old. This is a simple heuristic and may behave differently outside regular trading hours.

### Outlier Interpretation

Statistical anomalies are not necessarily data errors. Unusual price changes may reflect genuine market events.

### Machine Learning Limitations

The next-minute price-direction prediction task is noisy. Model accuracy alone does not establish profitability, and the model may perform differently under changing market conditions.

### Database Scalability

As the number of price bars grows, indexing, query optimization, retention policies, and possible time-based partitioning may become increasingly important.

### Historical Time Windows

The latest full-day view is based on the date of the newest stored bar. Depending on the data available, this may not correspond to the latest completed exchange trading session.

---

## Future Improvements

Potential extensions include:

- Add official exchange-calendar support for holidays and early closes.
- Introduce additional technical indicators and market features.
- Add configurable anomaly thresholds.
- Track anomaly outcomes to evaluate detection quality.
- Add model versioning and feature monitoring.
- Compare online learning against periodically retrained models.
- Add automated data-quality checks and ingestion alerts.
- Introduce connection pooling and query optimization.
- Add historical-data retention and archiving policies.
- Implement authentication and role-based access to the dashboard.
- Add automated tests for the ingestion and analytics pipelines.
- Use Azure monitoring services to track application errors and execution latency.

---

## Team Members

This project was developed by:

- **Venkata Puneeth Sriramaneni**
- **Christopher Mavros**
- **Rylie Fischer**

---

## Project Deliverables

The project demonstrates the following deliverables:

1. A relational database deployed on Azure PostgreSQL.
2. An automated market-data ingestion pipeline.
3. A Streamlit dashboard connected to PostgreSQL.
4. A statistical outlier detection component.
5. An online machine learning component with evaluation metrics.
6. A final project report.
7. A five-minute video presentation demonstrating the system, architecture, implementation choices, and results.

---

## Conclusion

The Live Stock Market Monitor demonstrates an end-to-end streaming analytics architecture built around Azure Database for PostgreSQL.

By combining automated market-data ingestion, relational storage, interactive visualization, robust statistical anomaly detection, and online machine learning, the project transforms incoming stock observations into useful analytical information.

The dashboard provides visibility into market behavior, ingestion activity, unusual observations, and model performance, while the underlying cloud architecture supports continuous data collection and analysis.

The project provides a practical foundation for exploring streaming data engineering, cloud database design, near-real-time visualization, anomaly detection, and incremental machine learning.