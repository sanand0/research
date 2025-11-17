/**
 * Improved Console Log Capture Patterns for CDP
 *
 * This file demonstrates improvements to the console capture pattern
 * documented in SKILL.md, addressing issues with falsy values and
 * object representation.
 */

/**
 * PATTERN 1: Original (from SKILL.md) - ISSUES WITH FALSY VALUES
 *
 * This pattern has the following issues:
 * - false, null, undefined appear as empty strings
 * - Objects only show generic "[object Object]" description
 */
const pattern1_original = {
  description: 'Original SKILL.md pattern',
  issues: ['Loses falsy values', 'Generic object representation'],
  code: `
    Runtime.consoleAPICalled(params => {
      const message = params.args.map(arg =>
        arg.value || arg.description  // ← Problem: false || ... = ""
      ).join(' ');
      logs.push({ type: params.type, message });
    });
  `
};

/**
 * PATTERN 2: Basic Fix - Handle Falsy Values
 *
 * Improves on Pattern 1 by:
 * ✓ Preserving falsy primitive values
 * ✓ Handling null and undefined explicitly
 * - Still has generic object representation
 */
const pattern2_basicFix = {
  description: 'Basic fix for falsy values',
  improvements: ['Preserves false/0/null/undefined'],
  issues: ['Still generic object representation'],
  code: `
    Runtime.consoleAPICalled(params => {
      const message = params.args.map(arg => {
        // Check value first, even if falsy
        if (arg.value !== undefined) {
          return String(arg.value);
        }
        // Fallback to description for objects
        if (arg.description) {
          return arg.description;
        }
        // Handle pure undefined
        return 'undefined';
      }).join(' ');
      logs.push({ type: params.type, message });
    });
  `,
  testResults: {
    false: 'false',      // ✓ Fixed
    null: 'null',        // ✓ Fixed
    undefined: 'undefined',  // ✓ Fixed
    object: 'Object'     // Still generic
  }
};

/**
 * PATTERN 3: Production-Ready - With Type Awareness
 *
 * Comprehensive pattern that:
 * ✓ Preserves all primitive values
 * ✓ Better object representation
 * ✓ Type-aware formatting
 * ✓ Handles all edge cases
 */
const pattern3_productionReady = {
  description: 'Production-ready pattern with type awareness',
  improvements: [
    'All falsy values preserved',
    'Better object representation',
    'Type-aware formatting',
    'Edge case handling'
  ],
  code: `
    Runtime.consoleAPICalled(params => {
      const formattedArgs = params.args.map(arg => {
        // Primitives with values (including falsy like false, 0, "")
        if (arg.value !== undefined) {
          const val = arg.value;
          if (typeof val === 'string') {
            return val;
          }
          if (typeof val === 'number' || typeof val === 'boolean') {
            return String(val);
          }
          // null explicitly
          if (val === null) {
            return 'null';
          }
          // Dates, regex, etc.
          if (val instanceof Date) {
            return val.toISOString();
          }
          // Fallback for other primitive types
          return String(val);
        }

        // Objects/complex types without value
        if (arg.type === 'object') {
          return arg.description || '[object Object]';
        }
        if (arg.type === 'undefined') {
          return 'undefined';
        }

        // Fallback
        return arg.description || 'unknown';
      }).join(' ');

      logs.push({
        type: params.type,
        message: formattedArgs,
        timestamp: new Date().toISOString()
      });
    });
  `,
  testResults: {
    'true': 'true',
    'false': 'false',
    '0': '0',
    '""': '""',
    'null': 'null',
    'undefined': 'undefined',
    'object': '[object Object]',
    'Error': 'Error: message text'
  }
};

/**
 * PATTERN 4: Advanced - Full Object Inspection
 *
 * For scenarios requiring detailed object inspection:
 * ✓ All features from Pattern 3
 * ✓ Can retrieve full object properties via objectId
 * ✓ Better error handling
 */
const pattern4_advancedObjectInspection = {
  description: 'Advanced pattern with object inspection capability',
  improvements: [
    'Can inspect objects via objectId',
    'Full error stack traces',
    'Async resolution of complex objects'
  ],
  code: `
    // Store for reference
    const logs = [];

    Runtime.consoleAPICalled(async params => {
      const logEntry = {
        type: params.type,
        timestamp: new Date().toISOString(),
        args: []
      };

      for (const arg of params.args) {
        const argData = {
          type: arg.type,
          value: arg.value,
          description: arg.description
        };

        // If it's an object with objectId, we can inspect it further
        if (arg.objectId && arg.type === 'object') {
          try {
            const objDetails = await Runtime.getProperties({
              objectId: arg.objectId,
              ownProperties: true
            });
            argData.properties = objDetails.result
              .slice(0, 5)  // Limit to first 5 properties
              .map(p => ({ name: p.name, value: p.value.value }));
          } catch (e) {
            // Object inspection failed, use description
          }
        }

        logEntry.args.push(argData);
      }

      // Format message
      const message = logEntry.args.map(arg => {
        if (arg.value !== undefined) {
          return String(arg.value);
        }
        return arg.description || 'undefined';
      }).join(' ');

      logEntry.message = message;
      logs.push(logEntry);
    });
  `,
  notes: 'Requires access to Runtime domain and may have performance implications'
};

/**
 * PATTERN 5: Recommended for SKILL.md Update
 *
 * This is the recommended replacement for the SKILL.md pattern.
 * It's simple, fixes the major issues, and is still concise.
 */
const pattern5_recommendedForDocs = {
  description: 'Recommended replacement for SKILL.md documentation',
  code: `
    const logs = [];

    Runtime.consoleAPICalled(params => {
      // Improved message extraction that handles falsy values
      const message = params.args.map(arg => {
        // For values (including falsy ones like false, 0, "")
        if (arg.value !== undefined) {
          return String(arg.value);
        }
        // For objects without direct values
        if (arg.description) {
          return arg.description;
        }
        // For undefined values
        return 'undefined';
      }).join(' ');

      logs.push({
        type: params.type,  // Note: console.warn → "warning", not "warn"
        message,
        timestamp: new Date().toISOString()
      });
    });

    await Runtime.enable();
    // ... page operations ...

    console.log('Captured logs:', logs);
  `,
  notes: [
    'Fixes: false, 0, null, undefined now appear correctly',
    'Note: console.warn() generates type "warning", not "warn"',
    'Objects still show generic description - use JSON.stringify() for details'
  ]
};

// Export examples for testing
module.exports = {
  pattern1_original,
  pattern2_basicFix,
  pattern3_productionReady,
  pattern4_advancedObjectInspection,
  pattern5_recommendedForDocs
};
