FROM eclipse-temurin:11-jre
WORKDIR /app
COPY target/payment-mock-1.0.0.jar app.jar
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "app.jar", "--server.port=8081"]
