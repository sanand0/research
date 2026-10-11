# Build the static binary on the host first (just build-native).
FROM scratch
COPY .build/inspect-server /inspect-server
USER 65532:65532
EXPOSE 8080
ENV PORT=8080
ENTRYPOINT ["/inspect-server"]
