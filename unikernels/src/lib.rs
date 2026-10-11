//! Runtime-independent HTTP contract, shared by Linux and WASI adapters.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

pub const MAX_BODY: usize = 1024 * 1024;

/// Return (HTTP status, JSON response). Hashes are over the original request bytes.
pub fn handle(method: &str, path: &str, body: &[u8]) -> (u16, String) {
    if body.len() > MAX_BODY {
        return (413, json!({"error": "body too large"}).to_string());
    }
    if method == "GET" && path == "/health" {
        return (200, json!({"status": "ok"}).to_string());
    }
    if method != "POST" || path != "/inspect" {
        return (404, json!({"error": "not found"}).to_string());
    }
    match serde_json::from_slice::<Value>(body) {
        Ok(value) => {
            let (kind, items) = match value {
                Value::Null => ("null", 0),
                Value::Bool(_) => ("boolean", 0),
                Value::Number(_) => ("number", 0),
                Value::String(_) => ("string", 0),
                Value::Array(items) => ("array", items.len()),
                Value::Object(fields) => ("object", fields.len()),
            };
            let sha256 = format!("{:x}", Sha256::digest(body));
            (200, json!({"bytes": body.len(), "items": items, "sha256": sha256, "type": kind}).to_string())
        }
        Err(_) => (400, json!({"error": "invalid json"}).to_string()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn objects_and_hash() {
        let input = br#"{"a":1,"b":true}"#;
        let (status, response) = handle("POST", "/inspect", input);
        assert_eq!(status, 200);
        let value: Value = serde_json::from_str(&response).unwrap();
        assert_eq!(value["type"], "object");
        assert_eq!(value["items"], 2);
        assert_eq!(value["bytes"], input.len());
        assert_eq!(value["sha256"].as_str().unwrap().len(), 64);
    }

    #[test]
    fn invalid_and_oversize() {
        assert_eq!(handle("POST", "/inspect", b"{").0, 400);
        assert_eq!(handle("POST", "/inspect", &vec![b' '; MAX_BODY + 1]).0, 413);
        assert_eq!(handle("GET", "/health", &[]).0, 200);
        assert_eq!(handle("GET", "/missing", &[]).0, 404);
    }

    #[test]
    fn array_and_scalar() {
        assert_eq!(serde_json::from_str::<Value>(&handle("POST", "/inspect", b"[1,2,3]").1).unwrap()["items"], 3);
        assert_eq!(serde_json::from_str::<Value>(&handle("POST", "/inspect", b"true").1).unwrap()["type"], "boolean");
    }
}
