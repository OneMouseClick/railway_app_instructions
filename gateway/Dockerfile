FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /build
COPY pom.xml .
COPY gateway ./gateway
RUN mvn -q -DskipTests package

FROM eclipse-temurin:21-jre-alpine

RUN apk add --no-cache wget \
    && addgroup --system --gid 1001 railway \
    && adduser --system --uid 1001 --ingroup railway railway

WORKDIR /app

COPY --from=build /build/gateway/target/gateway-*.jar app.jar
RUN chown railway:railway /app/app.jar

USER railway:railway

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=5 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health/liveness || exit 1

ENTRYPOINT ["java", \
            "-XX:+UseZGC", \
            "-XX:MaxRAMPercentage=75.0", \
            "-XX:+ExitOnOutOfMemoryError", \
            "-Djava.security.egd=file:/dev/./urandom", \
            "-jar", "app.jar"]
