# Transaction Portfolio Dashboard - Refactor Tasks

## Phase 1: Create Transaction Classification System
Create abstract transaction classifier with TransactionEffect enum and base class defining methods for transaction mapping, phantom position detection, share effect calculation, and cost basis calculation.

## Phase 2: Project Cleanup and Reorganization
Move debug CSV files to debug folder, delete unused files, reorganize adapter hierarchy into src/adapters/ibi/, update imports, fix hardcoded config paths.

## Phase 3: Implement IBI Transaction Classifier
Create IBI-specific classifier handling all 21 transaction types, positive-quantity quirks, phantom position detection with tax keywords, and cost basis calculations for deposits and bonuses.

## Phase 4: Update IBI Adapter with Classification
Refactor IBIAdapter transform method to use classifier and add metadata columns for transaction_effect, is_phantom, share_direction, share_quantity_abs, and cost_basis.

## Phase 5: Refactor Portfolio Builder
Update PortfolioBuilder to use classifier metadata instead of hardcoded logic, simplify transaction processing using is_phantom and cost_basis fields.

## Phase 6: Add Transaction Model Validation
Add Pydantic validators to Transaction model for quantity, price, and currency, plus optional classifier metadata fields.

## Phase 7: Implement Error Handling System
Create custom exceptions, standardize error handling across adapters, add input validation for Excel files, and implement user-friendly error messages.

## Phase 8: Add Comprehensive Logging
Replace print statements with structured logging, add log levels, create logging configuration.

## Phase 9: Create Test Fixtures and Unit Tests
Create tests/fixtures with sample transactions, implement unit tests for classifier with all 21 transaction types, phantom detection, and cost basis calculations.

## Phase 10: Validation Testing and Documentation
Run full portfolio validation against real data, update CLAUDE.md with new architecture, create TRANSACTION_TYPES.md reference guide documenting IBI quirks.
