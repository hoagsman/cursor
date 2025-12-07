"""
Excel Logger
Records all trading activity, performance metrics, and analytics to Excel.
Supports multiple sheets for different data views.
"""

from decimal import Decimal
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import LineChart, BarChart, Reference
from loguru import logger

from src.core.trade_executor import RoundResult, TradeGroupResult, TradeStatus


class ExcelLogger:
    """
    Comprehensive Excel logging for trading activity.
    
    Creates and maintains an Excel workbook with:
    - Trade Log: All individual trades
    - Round Summary: Results by trading round
    - Daily Summary: Daily P&L
    - Path Analysis: Most profitable paths
    - Fee Analysis: Fee breakdown
    """
    
    # Sheet names
    TRADES_SHEET = "Trade Log"
    ROUNDS_SHEET = "Round Summary"
    DAILY_SHEET = "Daily Summary"
    PATHS_SHEET = "Path Analysis"
    FEES_SHEET = "Fee Analysis"
    PERFORMANCE_SHEET = "Performance"
    
    def __init__(self, file_path: str):
        """
        Initialize the Excel logger.
        
        Args:
            file_path: Path to the Excel file
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._ensure_workbook_exists()
        
    def _ensure_workbook_exists(self) -> None:
        """Create workbook with all sheets if it doesn't exist."""
        if not self.file_path.exists():
            self._create_new_workbook()
            logger.info(f"Created new Excel log at {self.file_path}")
    
    def _create_new_workbook(self) -> None:
        """Create a new workbook with all required sheets."""
        wb = Workbook()
        
        # Remove default sheet
        if 'Sheet' in wb.sheetnames:
            del wb['Sheet']
        
        # Create sheets with headers
        sheets_config = {
            self.TRADES_SHEET: [
                'Timestamp', 'Round ID', 'Group ID', 'Trade #', 'Product',
                'Side', 'Size', 'Price', 'Fee', 'Status', 'Net Amount'
            ],
            self.ROUNDS_SHEET: [
                'Timestamp', 'Round ID', 'Groups Executed', 'Successful',
                'Failed', 'Start Amount', 'End Amount', 'Total Fees',
                'Net Profit', 'Profit %', 'Duration (s)'
            ],
            self.DAILY_SHEET: [
                'Date', 'Start Balance', 'End Balance', 'Total Profit',
                'Total Fees', 'Net Profit', 'Rounds', 'Trades',
                'Win Rate %', 'Avg Profit/Trade'
            ],
            self.PATHS_SHEET: [
                'Path', 'Chain Length', 'Times Used', 'Total Profit',
                'Avg Profit %', 'Success Rate %', 'Avg Execution Time',
                'Last Used'
            ],
            self.FEES_SHEET: [
                'Date', 'Product', 'Total Fees', 'Trade Count',
                'Avg Fee', 'Fee as % of Volume'
            ],
            self.PERFORMANCE_SHEET: [
                'Metric', 'Value', 'Notes'
            ]
        }
        
        for sheet_name, headers in sheets_config.items():
            ws = wb.create_sheet(sheet_name)
            self._write_header_row(ws, headers)
        
        wb.save(self.file_path)
    
    def _write_header_row(self, ws, headers: List[str]) -> None:
        """Write styled header row to worksheet."""
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='2B579A', end_color='2B579A', fill_type='solid')
        header_alignment = Alignment(horizontal='center', vertical='center')
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
            
            # Auto-width (approximate)
            ws.column_dimensions[cell.column_letter].width = max(len(header) + 2, 12)
    
    def log_trade_group(self, result: TradeGroupResult) -> None:
        """
        Log a single trade group execution.
        
        Args:
            result: TradeGroupResult from execution
        """
        try:
            wb = load_workbook(self.file_path)
            ws = wb[self.TRADES_SHEET]
            
            for i, trade in enumerate(result.trades):
                row = [
                    result.timestamp.isoformat(),
                    result.group_id.split('_group_')[0] if '_group_' in result.group_id else result.group_id,
                    result.group_id,
                    i + 1,
                    trade.product_id,
                    trade.side,
                    float(trade.size),
                    float(trade.price),
                    float(trade.fee),
                    trade.status,
                    float(trade.total_cost)
                ]
                ws.append(row)
            
            wb.save(self.file_path)
            
        except Exception as e:
            logger.error(f"Failed to log trade group: {e}")
    
    def log_round(self, result: RoundResult) -> None:
        """
        Log a complete trading round.
        
        Args:
            result: RoundResult from execution
        """
        try:
            wb = load_workbook(self.file_path)
            
            # Log to rounds sheet
            ws = wb[self.ROUNDS_SHEET]
            
            total_duration = sum(g.execution_time for g in result.group_results)
            
            row = [
                result.timestamp.isoformat(),
                result.round_id,
                len(result.group_results),
                result.successful_groups,
                result.failed_groups,
                float(result.total_start),
                float(result.total_end),
                float(result.total_fees),
                float(result.total_profit),
                float((result.total_profit / result.total_start) * 100) if result.total_start > 0 else 0,
                total_duration
            ]
            ws.append(row)
            
            # Log each group's trades
            for group_result in result.group_results:
                self.log_trade_group(group_result)
            
            wb.save(self.file_path)
            logger.debug(f"Logged round {result.round_id} to Excel")
            
        except Exception as e:
            logger.error(f"Failed to log round: {e}")
    
    def update_daily_summary(
        self,
        date: datetime,
        start_balance: Decimal,
        end_balance: Decimal,
        total_fees: Decimal,
        rounds: int,
        trades: int,
        wins: int
    ) -> None:
        """
        Update daily summary sheet.
        
        Args:
            date: Date of trading
            start_balance: Starting balance
            end_balance: Ending balance
            total_fees: Total fees paid
            rounds: Number of rounds executed
            trades: Number of trades executed
            wins: Number of profitable trades
        """
        try:
            wb = load_workbook(self.file_path)
            ws = wb[self.DAILY_SHEET]
            
            profit = end_balance - start_balance
            net_profit = profit - total_fees
            win_rate = (wins / trades * 100) if trades > 0 else 0
            avg_profit = float(profit / trades) if trades > 0 else 0
            
            row = [
                date.strftime('%Y-%m-%d'),
                float(start_balance),
                float(end_balance),
                float(profit),
                float(total_fees),
                float(net_profit),
                rounds,
                trades,
                win_rate,
                avg_profit
            ]
            
            # Check if date already exists, update if so
            date_str = date.strftime('%Y-%m-%d')
            found = False
            for row_num in range(2, ws.max_row + 1):
                if ws.cell(row=row_num, column=1).value == date_str:
                    for col, value in enumerate(row, 1):
                        ws.cell(row=row_num, column=col, value=value)
                    found = True
                    break
            
            if not found:
                ws.append(row)
            
            wb.save(self.file_path)
            
        except Exception as e:
            logger.error(f"Failed to update daily summary: {e}")
    
    def update_path_analysis(self, path_stats: Dict[str, Dict]) -> None:
        """
        Update path analysis sheet with aggregated statistics.
        
        Args:
            path_stats: Dictionary of path statistics
        """
        try:
            wb = load_workbook(self.file_path)
            ws = wb[self.PATHS_SHEET]
            
            # Clear existing data (keep header)
            for row in range(2, ws.max_row + 1):
                for col in range(1, ws.max_column + 1):
                    ws.cell(row=row, column=col, value=None)
            
            # Write new data
            row_num = 2
            for path_str, stats in path_stats.items():
                row = [
                    path_str,
                    stats.get('chain_length', 0),
                    stats.get('times_used', 0),
                    stats.get('total_profit', 0),
                    stats.get('avg_profit_percent', 0),
                    stats.get('success_rate', 0),
                    stats.get('avg_execution_time', 0),
                    stats.get('last_used', '')
                ]
                for col, value in enumerate(row, 1):
                    ws.cell(row=row_num, column=col, value=value)
                row_num += 1
            
            wb.save(self.file_path)
            
        except Exception as e:
            logger.error(f"Failed to update path analysis: {e}")
    
    def update_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Update performance metrics sheet.
        
        Args:
            metrics: Dictionary of performance metrics
        """
        try:
            wb = load_workbook(self.file_path)
            ws = wb[self.PERFORMANCE_SHEET]
            
            # Clear existing data (keep header)
            for row in range(2, ws.max_row + 1):
                for col in range(1, ws.max_column + 1):
                    ws.cell(row=row, column=col, value=None)
            
            # Write metrics
            row_num = 2
            for metric, value in metrics.items():
                ws.cell(row=row_num, column=1, value=metric)
                ws.cell(row=row_num, column=2, value=str(value))
                row_num += 1
            
            # Add timestamp
            ws.cell(row=row_num, column=1, value='Last Updated')
            ws.cell(row=row_num, column=2, value=datetime.now().isoformat())
            
            wb.save(self.file_path)
            
        except Exception as e:
            logger.error(f"Failed to update performance metrics: {e}")
    
    def add_chart_to_daily(self) -> None:
        """Add a profit chart to the daily summary sheet."""
        try:
            wb = load_workbook(self.file_path)
            ws = wb[self.DAILY_SHEET]
            
            if ws.max_row < 3:  # Need at least 2 data points
                return
            
            # Create profit line chart
            chart = LineChart()
            chart.title = "Daily Net Profit"
            chart.style = 10
            chart.y_axis.title = "Profit ($)"
            chart.x_axis.title = "Date"
            
            # Data reference
            data = Reference(ws, min_col=6, min_row=1, max_row=ws.max_row)
            dates = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
            
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(dates)
            
            ws.add_chart(chart, "L2")
            
            wb.save(self.file_path)
            
        except Exception as e:
            logger.error(f"Failed to add chart: {e}")
    
    def export_to_csv(self, sheet_name: str, output_path: str) -> None:
        """
        Export a sheet to CSV format.
        
        Args:
            sheet_name: Name of sheet to export
            output_path: Path for CSV output
        """
        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            df.to_csv(output_path, index=False)
            logger.info(f"Exported {sheet_name} to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
    
    def get_dataframe(self, sheet_name: str) -> pd.DataFrame:
        """
        Get sheet data as pandas DataFrame.
        
        Args:
            sheet_name: Name of sheet to read
            
        Returns:
            DataFrame with sheet data
        """
        return pd.read_excel(self.file_path, sheet_name=sheet_name)
