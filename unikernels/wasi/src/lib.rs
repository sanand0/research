//! WASI HTTP P2 adapter: same inspect_core::handle contract as the native server.
use http_body_util::BodyExt;
use wstd::http::{Body, Request, Response, Result};

#[wstd::http_server]
async fn main(req: Request<Body>) -> Result<Response<Body>> {
    let method = req.method().as_str().to_string();
    let path = req.uri().path().to_string();
    let mut incoming = req.into_body().into_boxed_body();
    let mut body = Vec::new();
    while let Some(frame) = incoming.frame().await {
        if let Ok(data) = frame?.into_data() {
            if body.len() + data.len() > inspect_core::MAX_BODY {
                body.resize(inspect_core::MAX_BODY + 1, 0);
                break;
            }
            body.extend_from_slice(&data);
        }
    }
    let (status, response) = inspect_core::handle(&method, &path, &body);
    Ok(Response::builder()
        .status(status)
        .header("content-type", "application/json")
        .body(response.into())
        .expect("valid response"))
}
