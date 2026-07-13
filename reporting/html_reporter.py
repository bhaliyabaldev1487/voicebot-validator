"""
reporting/html_reporter.py

Generate a human-readable HTML validation report for Order Flow.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Dict, List


class HTMLReporter:
    """
    Renders validation result into an HTML report.
    """

    def write(
        self,
        result: Dict[str, Any],
        output_file: str,
    ) -> str:
        """
        Write HTML report to disk.

        Returns:
            output file path
        """
        html = self.render(result)

        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

        return str(path)

    def render(self, result: Dict[str, Any]) -> str:
        metadata = result.get("metadata", {})
        transcript = result.get("transcript", {})
        entities = result.get("entities", {})
        lookup = result.get("lookup", {})
        validation = result.get("validation", {})

        checks = validation.get("checks", [])
        success = validation.get("success", False)

        status_class = "pass" if success else "fail"
        status_text = "PASSED" if success else "FAILED"

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Voicebot Order Validation Report</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 24px;
      color: #222;
      background: #fafafa;
    }}
    h1, h2, h3 {{
      margin-bottom: 8px;
    }}
    .card {{
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 18px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    .status {{
      display: inline-block;
      padding: 8px 14px;
      border-radius: 999px;
      font-weight: bold;
      color: #fff;
      margin-bottom: 12px;
    }}
    .pass {{
      background: #2e7d32;
    }}
    .fail {{
      background: #c62828;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
    }}
    th, td {{
      border: 1px solid #ddd;
      padding: 10px;
      text-align: left;
      vertical-align: top;
      font-size: 14px;
    }}
    th {{
      background: #f5f5f5;
    }}
    .mono {{
      font-family: Menlo, Consolas, monospace;
      white-space: pre-wrap;
      word-break: break-word;
      background: #f8f8f8;
      border-radius: 6px;
      padding: 10px;
    }}
    .check-pass {{
      color: #2e7d32;
      font-weight: bold;
    }}
    .check-fail {{
      color: #c62828;
      font-weight: bold;
    }}
    .section-title {{
      margin-top: 0;
    }}
  </style>
</head>
<body>

  <h1>Voicebot Order Validation Report</h1>

  <div class="card">
    <div class="status {status_class}">{status_text}</div>
    <h2 class="section-title">Validation Summary</h2>
    <p><strong>Summary:</strong> {escape(str(validation.get("summary", "")))}</p>
    <p><strong>Passed checks:</strong> {escape(str(validation.get("passed_checks", 0)))}</p>
    <p><strong>Failed checks:</strong> {escape(str(validation.get("failed_checks", 0)))}</p>
  </div>

  <div class="card">
    <h2 class="section-title">Metadata</h2>
    {self._kv_table(metadata)}
  </div>

  <div class="card">
    <h2 class="section-title">Extracted Entities</h2>
    {self._kv_table(entities)}
  </div>

  <div class="card">
    <h2 class="section-title">Lookup Result</h2>
    <h3>Lookup Meta</h3>
    {self._kv_table({
        "success": lookup.get("success"),
        "lookup_method": lookup.get("lookup_method"),
        "message": lookup.get("message"),
    })}

    <h3>Customer</h3>
    {self._kv_table(lookup.get("customer") or {})}

    <h3>Order</h3>
    {self._kv_table(lookup.get("order") or {})}
  </div>

  <div class="card">
    <h2 class="section-title">Validation Checks</h2>
    {self._checks_table(checks)}
  </div>

  <div class="card">
    <h2 class="section-title">Transcript - Customer</h2>
    <div class="mono">{escape(str(transcript.get("customer_text", "")))}</div>
  </div>

  <div class="card">
    <h2 class="section-title">Transcript - Bot</h2>
    <div class="mono">{escape(str(transcript.get("bot_text", "")))}</div>
  </div>

  <div class="card">
    <h2 class="section-title">Transcript - Full Conversation</h2>
    <div class="mono">{escape(str(transcript.get("full_text", "")))}</div>
  </div>

</body>
</html>
"""
        return html

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _kv_table(self, data: Dict[str, Any]) -> str:
        if not data:
            return "<p>No data available.</p>"

        rows = []
        for key, value in data.items():
            rows.append(
                f"<tr><th>{escape(str(key))}</th><td>{escape(self._stringify(value))}</td></tr>"
            )

        return f"""
<table>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
"""

    def _checks_table(self, checks: List[Dict[str, Any]]) -> str:
        if not checks:
            return "<p>No validation checks available.</p>"

        rows = []
        for check in checks:
            passed = bool(check.get("passed"))
            css = "check-pass" if passed else "check-fail"
            label = "PASS" if passed else "FAIL"

            rows.append(
                f"""
<tr>
  <td>{escape(str(check.get("name", "")))}</td>
  <td class="{css}">{label}</td>
  <td>{escape(self._stringify(check.get("expected")))}</td>
  <td>{escape(self._stringify(check.get("actual")))}</td>
  <td>{escape(self._stringify(check.get("details")))}</td>
</tr>
"""
            )

        return f"""
<table>
  <thead>
    <tr>
      <th>Check</th>
      <th>Status</th>
      <th>Expected</th>
      <th>Actual</th>
      <th>Details</th>
    </tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
"""

    @staticmethod
    def _stringify(value: Any) -> str:
        if value is None:
            return ""
        return str(value)