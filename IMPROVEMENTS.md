# Improvements Plan

## 1. Performance Optimization
- **Parallel Question Generation**: Use `concurrent.futures.ThreadPoolExecutor` to call the LLM for 15 questions simultaneously.
- **Caching**: Improve cache management to allow manual clear of cache.

## 2. Robustness & Reliability
- **Robust JSON Parsing**: Implement a regex-based parser to extract JSON content from LLM responses, handling both raw JSON and markdown blocks.
- **Error Handling**: Implement a retry mechanism for LLM calls in case of timeouts or rate limits.

## 3. Maintainability & Clean Code
- **Configuration File**: Create a `config.py` to store:
  - LLM Model Name
  - Temperature
  - Subjects List
  - Cache Expiry
- **Logging**: Implement a standardized logging setup.
- **Code Cleanup**: Remove commented-out code blocks.

## 4. UI/UX Improvements
- **Progress Indicators**: Show a progress bar while 15 questions are being generated.
- **Responsive Styling**: Improve the CSS to be more responsive on different screen sizes.

## 5. Architecture Improvements
- **Service Separation**: Move question generation logic to a dedicated `generator.py` module.
