#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Runner Script for Pet E-Commerce Platform

This script provides a convenient interface to run the complete test suite
with various configurations and reporting options.

Usage:
    python scripts/run_tests.py                    # Run all tests
    python scripts/run_tests.py --coverage         # Run with coverage report
    python scripts/run_tests.py --verbose          # Run with detailed output
    python scripts/run_tests.py --quick            # Run without coverage (faster)
    python scripts/run_tests.py --unit             # Run only unit tests
    python scripts/run_tests.py --integration      # Run only integration tests
    python scripts/run_tests.py --e2e              # Run only E2E tests
    python scripts/run_tests.py --failed           # Re-run only failed tests
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


def run_command(cmd, description):
    """Execute a shell command and print status."""
    separator = "=" * 70
    print(f"\n{separator}")
    print(f"[TEST] {description}")
    print(f"{separator}\n")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Run Pet E-Commerce test suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py                    # Run all tests with coverage
  python scripts/run_tests.py --quick            # Run all tests (no coverage)
  python scripts/run_tests.py --verbose          # Run with detailed output
  python scripts/run_tests.py --unit             # Run only unit tests
  python scripts/run_tests.py --integration      # Run only integration tests
  python scripts/run_tests.py --e2e              # Run only E2E tests
  python scripts/run_tests.py --failed           # Re-run failed tests
  python scripts/run_tests.py --html             # Generate HTML coverage report
        """
    )
    
    # Test selection
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        '--unit', 
        action='store_true', 
        help='Run only unit tests'
    )
    test_group.add_argument(
        '--integration', 
        action='store_true', 
        help='Run only integration tests'
    )
    test_group.add_argument(
        '--e2e', 
        action='store_true', 
        help='Run only end-to-end tests'
    )
    test_group.add_argument(
        '--failed', 
        action='store_true', 
        help='Re-run only failed tests from last run'
    )
    
    # Output options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show verbose output with individual test results'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Minimal output (only test summary)'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run tests without coverage (faster execution)'
    )
    
    # Coverage options
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Run with coverage report (default behavior)'
    )
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML coverage report in htmlcov/'
    )
    parser.add_argument(
        '--no-coverage',
        action='store_true',
        help='Skip coverage reporting'
    )
    
    # Additional options
    parser.add_argument(
        '--stop-on-failure', '-x',
        action='store_true',
        help='Stop execution on first test failure'
    )
    parser.add_argument(
        '--markers', '-m',
        type=str,
        help='Run tests matching given mark expression (e.g., "slow")'
    )
    parser.add_argument(
        '--keyword', '-k',
        type=str,
        help='Run tests matching given keyword expression'
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd_parts = ['pytest']
    
    # Test selection
    if args.unit:
        cmd_parts.append('tests/unit/')
        description = "Running Unit Tests"
    elif args.integration:
        cmd_parts.append('tests/integration/')
        description = "Running Integration Tests"
    elif args.e2e:
        cmd_parts.append('tests/e2e/')
        description = "Running End-to-End Tests"
    elif args.failed:
        cmd_parts.append('--lf')  # last failed
        description = "Re-running Failed Tests"
    else:
        cmd_parts.append('tests/')
        description = "Running All Tests"
    
    # Coverage (enabled by default unless --quick or --no-coverage)
    if args.html:
        cmd_parts.extend(['--cov=app', '--cov-report=html', '--cov-report=term'])
        description += " with HTML Coverage Report"
    elif not args.quick and not args.no_coverage:
        cmd_parts.extend(['--cov=app', '--cov-report=term-missing'])
        description += " with Coverage"
    elif args.coverage:
        cmd_parts.extend(['--cov=app', '--cov-report=term'])
        description += " with Coverage"
    
    # Output verbosity
    if args.verbose:
        cmd_parts.append('-v')
    elif args.quiet:
        cmd_parts.append('-q')
    
    # Additional options
    if args.stop_on_failure:
        cmd_parts.append('-x')
    
    if args.markers:
        cmd_parts.extend(['-m', args.markers])
    
    if args.keyword:
        cmd_parts.extend(['-k', args.keyword])
    
    # Always show summary
    cmd_parts.append('--tb=short')
    
    # Build final command
    cmd = ' '.join(cmd_parts)
    
    # Print header
    separator = "=" * 70
    print(f"\n{separator}")
    print("Pet E-Commerce Platform - Test Suite Runner")
    print(separator)
    print(f"\nCommand: {cmd}\n")
    
    # Run tests
    exit_code = run_command(cmd, description)
    
    # Print footer
    print(f"\n{separator}")
    if exit_code == 0:
        print("[SUCCESS] All tests passed successfully!")
    else:
        print("[FAILURE] Some tests failed. Review output above.")
    
    if args.html and exit_code == 0:
        print("\n[COVERAGE] HTML coverage report generated in: htmlcov/index.html")
        print("           Open in browser to view detailed coverage.")
    
    print(f"{separator}\n")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
