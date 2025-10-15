# Transaction Portfolio Dashboard - Critical Refactoring Tasks

## Executive Summary

Refactor transaction portfolio dashboard to address critical architectural issues identified in comprehensive review. Focus on unifying adapter architecture, adding validation, and removing code duplication.

## Critical Issues to Fix

### 1. Duplicate Adapter Architecture (CRITICAL)
**Problem**: Two separate adapter hierarchies exist:
- `/adapters/` - Has BaseAdapter and IBIAdapter (properly inheriting)
- `/src/adapters/` - Has ActualPortfolioAdapter (doesn't inherit, duplicates logic)

**Solution**: Consolidate all adapters under `/src/adapters/`, ensure all inherit from BaseAdapter, remove duplication.

### 2. Missing Transaction Classification System (CRITICAL)
**Problem**: IBI-specific transaction logic scattered throughout codebase. Need generalized system.

**Solution**: Create TransactionClassifier class in `src/models/transaction_classifier.py` that encapsulates broker-specific transaction type logic.

### 3. Incomplete Phantom Position Detection (HIGH)
**Problem**: Only checks symbol prefix (999xxxx), misses tax entries like "מס ששולם".

**Solution**: Enhance phantom detection in builder.py to check both symbol pattern AND security name patterns.

### 4. Missing Input Validation (HIGH)
**Problem**: Transaction model allows invalid data (negative quantities/prices, any currency string).

**Solution**: Add Pydantic validators to Transaction model for quantity, execution_price, currency fields.

### 5. Project Cleanup (MEDIUM)
**Problem**: 18 debug CSV files and 5 test files cluttering root directory.

**Solution**: Move/delete debug files, organize test files into tests/ directory.

### 6. Unused Portfolio Model (MEDIUM)
**Problem**: `src/models/portfolio.py` (69 lines) is never used and doesn't match current Transaction properties.

**Solution**: Either adapt Portfolio model to current architecture or delete if truly unused.

### 7. Empty Directories (LOW)
**Problem**: `src/output/` and `src/visualization/` exist but are empty.

**Solution**: Remove empty directories or add placeholder files if planned for future use.

## Implementation Approach

1. **Unify Adapter Architecture** - Move all adapters to src/adapters/, ensure inheritance
2. **Add Transaction Classifier** - Extract classification logic into dedicated class
3. **Enhance Validation** - Add Pydantic validators and phantom detection
4. **Clean Project Structure** - Remove debug files, organize tests
5. **Error Handling** - Add comprehensive try-catch blocks in critical paths
6. **Documentation** - Update CLAUDE.md to reflect new architecture

## Success Criteria

- Single unified adapter hierarchy under src/adapters/
- All adapters inherit from BaseAdapter
- Transaction classifier handles all IBI quirks
- Input validation prevents invalid data
- Clean project structure (no debug files in root)
- All existing functionality still works correctly
- Portfolio calculations match IBI broker statements

## Priority

**Critical**: Tasks 1-2 (adapter unification, transaction classifier)
**High**: Tasks 3-4 (validation, phantom detection)
**Medium**: Tasks 5-6 (cleanup, unused code)
**Low**: Task 7 (empty directories)
