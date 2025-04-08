# DUADlyfter

## Finance Tracker Project

### Project Description
The Finance Tracker is a Python-based application designed to help users manage their financial movements. It allows users to track income and expenses, calculate totals, and automatically save or load data from a default CSV file.

### Features
- Add income and expense movements with categories.
- Calculate totals for income, expenses, and net balance.
- Automatically load and save data to a default CSV file.
- Modern and intuitive GUI for ease of use.

### How to Use
1. **Run the Application**:
   Navigate to the `week_17` folder and execute the `finance_tracker.py` file:
   ```bash
   python week_17/finance_tracker.py
   ```

2. **Add Movements**:
   - Use the "Add Expense" or "Add Income" buttons to add financial movements.
   - Specify the name, category, and amount for each movement.

3. **Add Categories**:
   - Click the "Add Category" button to define new categories for your movements.

4. **View Data**:
   - The financial data table displays all movements.

5. **Automatic Save**:
   - Data is automatically saved to a default CSV file (`finance_data.csv`) whenever movements are added.

6. **Automatic Load**:
   - The application automatically loads data from the default CSV file on startup.

### Requirements
- Python 3.8 or higher
- FreeSimpleGUI library

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/DUADlyfter.git
   ```
2. Navigate to the project directory:
   ```bash
   cd DUADlyfter
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Folder Structure
- **week_17**: Contains the Finance Tracker application.
  - `Gui`: GUI components for the application.
  - `DataHandler`: Handles CSV import/export operations.
  - `Utilities`: Helper functions for validation and debugging.
  - `Clases`: Core classes for financial movements and monthly summaries.
  - `Tests`: Unit tests for the application.

### Contribution
Feel free to fork the repository, make improvements, and submit a pull request.

### License
This project is licensed under the MIT License.
