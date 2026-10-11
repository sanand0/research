use inspect_core::{MAX_BODY, handle};
use std::io::Read;
use tiny_http::{Header, Response, Server, StatusCode};

fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let port = std::env::var("PORT").unwrap_or_else(|_| "8080".into());
    let server = Server::http(format!("0.0.0.0:{port}"))?;
    eprintln!("inspect-server listening on {port}");
    for mut request in server.incoming_requests() {
        let mut body = Vec::new();
        // take() bounds memory even for streaming or chunked request bodies.
        let mut input = request.as_reader().take((MAX_BODY + 1) as u64);
        let result = input.read_to_end(&mut body);
        let (status, response) = match result {
            Ok(_) => handle(request.method().as_str(), request.url().split('?').next().unwrap_or(""), &body),
            Err(_) => (400, r#"{"error":"cannot read body"}"#.to_string()),
        };
        let json_header = Header::from_bytes("Content-Type", "application/json").expect("static header");
        let reply = Response::from_string(response)
            .with_status_code(StatusCode(status))
            .with_header(json_header);
        if let Err(error) = request.respond(reply) {
            eprintln!("response error: {error}");
        }
    }
    Ok(())
}
