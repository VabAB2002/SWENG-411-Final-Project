# Overlap Display Duplicate Fix

## Date: November 22, 2025

## Issue
The Economics Minor detail page was showing duplicate entries in "Courses You've Already Completed":
- ECON 102
- ECON 302  
- ECON 304
- ECON471
- **ECON 471** (duplicate)

## Root Cause

The `calculate_overlap_courses` function in `recommendation_engine.py` was not properly normalizing course codes before checking for duplicates. 

For `dynamic_subset` rules:
1. The primary pool check adds courses from user history (e.g., "ECON 471")
2. The secondary pool check adds courses from the rule definition (e.g., "ECON471" without space)
3. The deduplication logic compared raw strings instead of normalized codes
4. Result: Both "ECON 471" and "ECON471" appeared in the list

## Solution Implemented

Updated three sections in `calculate_overlap_courses` function:

### 1. Primary Pool Check (Line ~384)
```python
# Check normalized codes to avoid duplicates like "ECON471" and "ECON 471"
if normalize_code(orig_code) not in [normalize_code(c) for c in overlapping_courses]:
    overlapping_courses.append(orig_code)
```

### 2. Secondary Pool Check (Line ~392-393)
```python
# Check normalized codes to avoid duplicates
if code_norm not in [normalize_code(c) for c in overlapping_courses]:
    overlapping_courses.append(course_code)
```

### 3. Final Deduplication (Line ~407-409)
```python
# Remove duplicates while preserving order (normalize before comparing)
for c in overlapping_courses:
    normalized = normalize_code(c)
    if normalized not in seen:
        seen.add(normalized)
        unique_overlapping.append(c)
```

## Test Results

**Before Fix:**
```
Courses You've Already Completed:
  ✓ ECON 102
  ✓ ECON 302
  ✓ ECON 304
  ✓ ECON471
  ✓ ECON 471  ← Duplicate
```

**After Fix:**
```
✅ Economics Minor - Fixed Overlap Display
============================================================
Gap Credits: 6.0 credits
Overlap Count: 4 courses

Courses You've Already Completed:
  ✓ ECON 102
  ✓ ECON 302
  ✓ ECON 304
  ✓ ECON471

============================================================
✅ No duplicates - FIXED!
```

## Impact

- ✅ Eliminates duplicate course display in detail page
- ✅ Correct overlap count (4 instead of 5)
- ✅ Works for all programs using `dynamic_subset` rules
- ✅ No impact on gap credit calculations (still accurate)

## Files Modified

- `backend/recommendation_engine.py` - Updated `calculate_overlap_courses` function (lines 368-412)

## Notes

- The `normalize_code` function removes spaces and converts to uppercase: "ECON 471" → "ECON471"
- This ensures consistent comparison regardless of how courses are formatted in different data sources
- The fix applies to all rule types but is most critical for `dynamic_subset` rules that combine primary and secondary pools

---

**Status:** ✅ **FIXED AND TESTED**

