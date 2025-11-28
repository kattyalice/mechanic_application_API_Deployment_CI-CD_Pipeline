Testing & Validation Summary

Part 3 of this project focused on improving the API’s reliability through structured testing, schema refinement, and clearer validation rules. My main goal was to ensure every endpoint behaves consistently and handles both correct and incorrect input properly.

A full suite of unittest tests was created for mechanics, inventory, and service tickets. Each test runs in a fresh in-memory database, which guarantees isolation and makes the results repeatable. The tests cover successful operations as well as common failure cases—such as missing data, invalid types, unauthorized access, and non-existent IDs. This provides strong assurance that each route responds correctly under real-world conditions.

Marshmallow schemas were cleaned up and corrected to match the updated models. This included fixing nested relationships, avoiding circular references, and enforcing required fields like VIN for service tickets and name for inventory items. These updates ensure that all input sent to the API is properly validated before reaching the database.

Several issues uncovered by the tests, such as missing authentication contexts, invalid field names, or incorrect error messages, were resolved by adjusting the route logic or schema configuration. This refinement step helped align the API’s behavior with the tests and improved overall consistency.

Together, the test suite and schema updates now act as documentation for how the API should function. They clearly define expected inputs, outputs, and error responses while ensuring the system is dependable and maintainable moving forward.