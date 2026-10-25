# ============================================================
# BUILD STAGE
# ============================================================

FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /app

# Copy Maven configuration first
COPY pom.xml .

# Download dependencies
RUN mvn dependency:go-offline

# Copy source code
COPY src ./src

# Build Spring Boot application
RUN mvn clean package -DskipTests


# ============================================================
# RUN STAGE
# ============================================================

FROM eclipse-temurin:21-jre

WORKDIR /app

# Copy generated JAR from build stage
COPY --from=build /app/target/*.jar app.jar

# Spring Boot port
EXPOSE 8081

# Start application
ENTRYPOINT ["java", "-jar", "app.jar"]