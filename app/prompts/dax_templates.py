# app/prompts/dax_templates.py
"""
This module contains DAX-specific prompt templates and examples
that can be used to generate better DAX formulas.
"""

# Common DAX patterns with descriptions
DAX_PATTERNS = {
    "year_to_date": {
        "description": "Calculate year-to-date totals",
        "template": """
CALCULATE(
    [Measure],
    DATESYTD('Date'[Date])
)
"""
    },
    "year_over_year": {
        "description": "Calculate year-over-year comparison",
        "template": """
VAR CurrentValue = [Measure]
VAR PriorValue = CALCULATE(
    [Measure],
    SAMEPERIODLASTYEAR('Date'[Date])
)
RETURN
    CurrentValue - PriorValue
"""
    },
    "year_over_year_percent": {
        "description": "Calculate year-over-year percentage change",
        "template": """
VAR CurrentValue = [Measure]
VAR PriorValue = CALCULATE(
    [Measure],
    SAMEPERIODLASTYEAR('Date'[Date])
)
RETURN
    DIVIDE(
        CurrentValue - PriorValue,
        PriorValue
    )
"""
    },
    "running_total": {
        "description": "Calculate running total",
        "template": """
CALCULATE(
    [Measure],
    DATESBETWEEN(
        'Date'[Date],
        FIRSTDATE('Date'[Date]),
        MAX('Date'[Date])
    )
)
"""
    },
    "moving_average": {
        "description": "Calculate moving average",
        "template": """
VAR NumPeriods = 3 // Change as needed
RETURN
AVERAGEX(
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -NumPeriods,
        MONTH // Change as needed (DAY, MONTH, QUARTER, YEAR)
    ),
    [Measure]
)
"""
    },
    "top_n": {
        "description": "Calculate Top N items by measure",
        "template": """
VAR TopN = 10 // Change as needed
VAR RankedTable = 
    ADDCOLUMNS(
        VALUES('Table'[Column]),
        "Rank", RANKX(VALUES('Table'[Column]), [Measure])
    )
RETURN
    CALCULATE(
        [Measure],
        FILTER(
            RankedTable,
            [Rank] <= TopN
        )
    )
"""
    },
    "filtered_total": {
        "description": "Calculate total with specific filter",
        "template": """
CALCULATE(
    [Measure],
    FILTER(
        ALL('Table'),
        'Table'[Column] = "Value"
    )
)
"""
    }
}

# Time intelligence patterns
TIME_INTELLIGENCE_PATTERNS = {
    "month_to_date": {
        "description": "Calculate month-to-date totals",
        "template": """
CALCULATE(
    [Measure],
    DATESMTD('Date'[Date])
)
"""
    },
    "quarter_to_date": {
        "description": "Calculate quarter-to-date totals",
        "template": """
CALCULATE(
    [Measure],
    DATESQTD('Date'[Date])
)
"""
    },
    "previous_month": {
        "description": "Calculate measure for the previous month",
        "template": """
CALCULATE(
    [Measure],
    PREVIOUSMONTH('Date'[Date])
)
"""
    },
    "previous_quarter": {
        "description": "Calculate measure for the previous quarter",
        "template": """
CALCULATE(
    [Measure],
    PREVIOUSQUARTER('Date'[Date])
)
"""
    },
    "previous_year": {
        "description": "Calculate measure for the previous year",
        "template": """
CALCULATE(
    [Measure],
    PREVIOUSYEAR('Date'[Date])
)
"""
    }
}

# Statistical patterns
STATISTICAL_PATTERNS = {
    "percentage_of_total": {
        "description": "Calculate percentage of total",
        "template": """
DIVIDE(
    [Measure],
    CALCULATE(
        [Measure],
        ALL('Table')
    )
)
"""
    },
    "percent_of_column_total": {
        "description": "Calculate percentage of column total",
        "template": """
DIVIDE(
    [Measure],
    CALCULATE(
        [Measure],
        ALLEXCEPT('Table', 'Table'[Column])
    )
)
"""
    },
    "variance": {
        "description": "Calculate variance between actual and budget",
        "template": """
[Actual Measure] - [Budget Measure]
"""
    },
    "variance_percent": {
        "description": "Calculate percentage variance",
        "template": """
DIVIDE(
    [Actual Measure] - [Budget Measure],
    [Budget Measure]
)
"""
    }
}