from form_builder.utils.helpers import generate_form_description
import os
import json

print(generate_form_description({
    "form_name": "Drill Form",
    "form_description": "Form to record Drill operations and shot hole details for shift-wise production reports.",
    "fields": [
      {
        "checked": "true",
        "description": "The name of the subsidiary managing this report",
        "disabled": "false",
        "label": "Name of Subsidiary",
        "name": "subsidiary_name",
        "placeholder": "Enter the name of the subsidiary",
        "required": "true",
        "rowIndex": 0,
        "type": "Text",
        "value": "",
        "variant": "Input"
      },
      {
        "checked": "true",
        "description": "The name of the mine where the report is being generated",
        "disabled": "false",
        "label": "Name of the Mine",
        "name": "mine_name",
        "placeholder": "Enter the name of the mine",
        "required": "true",
        "rowIndex": 0,
        "type": "Text",
        "value": "",
        "variant": "Input"
      },
      {
        "checked": "true",
        "description": "The area for which the report is being generated",
        "disabled": "false",
        "label": "Name of the Area",
        "name": "area_name",
        "placeholder": "Enter the name of the area",
        "required": "true",
        "rowIndex": 0,
        "type": "Text",
        "value": "",
        "variant": "Combobox"
      },
      {
        "checked": "true",
        "description": "The date for which the report is being prepared",
        "disabled": "false",
        "label": "Date",
        "name": "date",
        "placeholder": "Select the date",
        "required": "true",
        "rowIndex": 0,
        "type": "Date Picker",
        "value": "",
        "variant": "Date Picker"
      },
      {
        "checked": "true",
        "description": "The shift during which the report is applicable",
        "disabled": "false",
        "label": "Shift",
        "name": "shift",
        "placeholder": "Select the shift",
        "required": "true",
        "rowIndex": 0,
        "type": "Select",
        "value": "",
        "variant": "Combobox"
      },
      {
        "checked": "true",
        "description": "Name or number of the drill machine",
        "disabled": "false",
        "label": "Name/No.",
        "name": "drill_name_no",
        "placeholder": "Enter the drill name or number",
        "required": "true",
        "rowIndex": 0,
        "type": "Text",
        "value": "",
        "variant": "Input"
      },
      {
        "checked": "true",
        "description": "Bench number where drilling is being performed",
        "disabled": "false",
        "label": "Bench No.",
        "name": "bench_no",
        "placeholder": "Enter the bench number",
        "required": "true",
        "rowIndex": 0,
        "type": "Text",
        "value": "",
        "variant": "Input"
      },
      {
        "checked": "true",
        "description": "Working hours of the drill",
        "disabled": "false",
        "label": "Working Hours",
        "name": "working_hours",
        "placeholder": "Enter working hours",
        "required": "true",
        "rowIndex": 0,
        "type": "Number",
        "value": "",
        "variant": "Input"
      },
      {
        "checked": "true",
        "description": "Breakdown hours of the drill",
        "disabled": "false",
        "label": "BD Hours",
        "name": "bd_hours",
        "placeholder": "Enter breakdown hours",
        "required": "true",
        "rowIndex": 0,
        "type": "Number",
        "value": "",
        "variant": "Input"
      },
      {
        "checked": "true",
        "description": "Idle hours of the drill",
        "disabled": "false",
        "label": "Idle Hours",
        "name": "idle_hours",
        "placeholder": "Enter idle hours",
        "required": "true",
        "rowIndex": 0,
        "type": "Number",
        "value": "",
        "variant": "Input"
      },
      {
        "checked": "true",
        "description": "Bench hours for drilling operation",
        "disabled": "false",
        "label": "Bench Hours",
        "name": "bench_hours",
        "placeholder": "Enter bench hours",
        "required": "true",
        "rowIndex": 0,
        "type": "Number",
        "value": "",
        "variant": "Input"
      },
      {
        "checked": "true",
        "description": "Number of shot holes drilled",
        "disabled": "false",
        "label": "No. of Shot holes drilled",
        "name": "shot_holes_count",
        "placeholder": "Enter number of shot holes drilled",
        "required": "true",
        "rowIndex": 0,
        "type": "Number",
        "value": "",
        "variant": "Input"
      },
      {
        "checked": "true",
        "description": "Total drilling meters achieved",
        "disabled": "false",
        "label": "Drilling metre",
        "name": "drilling_meter",
        "placeholder": "Enter total drilling meters",
        "required": "true",
        "rowIndex": 0,
        "type": "Number",
        "value": "",
        "variant": "Input"
      },
      {
        "checked": "true",
        "description": "Total of all relevant metrics",
        "disabled": "false",
        "label": "Total",
        "name": "total",
        "placeholder": "Enter total",
        "required": "true",
        "rowIndex": 0,
        "type": "Number",
        "value": "",
        "variant": "Input"
      }
    ]
  }))