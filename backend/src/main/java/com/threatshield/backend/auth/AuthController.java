
package com.threatshield.backend.auth;

import com.threatshield.backend.security.JwtService;
import com.threatshield.backend.user.entity.Role;
import com.threatshield.backend.user.entity.User;
import com.threatshield.backend.user.repository.UserRepository;

import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "http://localhost:5173")
public class AuthController {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthController(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            JwtService jwtService) {

        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    // ============================================================
    // REGISTER
    // ============================================================

    @PostMapping("/register")
    public ResponseEntity<?> register(
            @RequestBody RegisterRequest request) {

        if (userRepository.existsByEmail(request.getEmail())) {

            return ResponseEntity.badRequest()
                    .body("Email already registered");
        }

        User user = new User(
                request.getName(),
                request.getEmail(),
                passwordEncoder.encode(request.getPassword()),
                request.getRole()
        );

        userRepository.save(user);

        return ResponseEntity.ok(
                "User registered successfully"
        );
    }

    // ============================================================
    // LOGIN
    // ============================================================

    @PostMapping("/login")
    public ResponseEntity<?> login(
            @RequestBody LoginRequest request) {

        // Find user by email
        User user = userRepository
                .findByEmail(request.getEmail())
                .orElse(null);

        // User doesn't exist
        if (user == null) {

            return ResponseEntity
                    .status(401)
                    .body("Invalid email or password");
        }

        // Compare entered password with BCrypt hash
        boolean passwordMatches =
                passwordEncoder.matches(
                        request.getPassword(),
                        user.getPassword()
                );

        // Password incorrect
        if (!passwordMatches) {

            return ResponseEntity
                    .status(401)
                    .body("Invalid email or password");
        }

        String token = jwtService.generateToken(
                user.getEmail(),
                user.getRole().name()
        );

        // Login successful
        return ResponseEntity.ok(
                new LoginResponse(
                        true,
                        "Login successful",
                        token,
                        user.getId(),
                        user.getName(),
                        user.getEmail(),
                        user.getRole()
                        
                )
        );
    }

    // ============================================================
    // REGISTER REQUEST
    // ============================================================

    public static class RegisterRequest {

        private String name;
        private String email;
        private String password;
        private Role role;

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }

        public Role getRole() {
            return role;
        }

        public void setRole(Role role) {
            this.role = role;
        }
    }

    // ============================================================
    // LOGIN REQUEST
    // ============================================================

    public static class LoginRequest {

        private String email;
        private String password;

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }
    }

    // ============================================================
    // LOGIN RESPONSE
    // ============================================================

    public static class LoginResponse {

        private boolean success;
        private String message;
        private Long id;
        private String name;
        private String email;
        private Role role;
        private String token;

        public LoginResponse(
                boolean success,
                String message,
                String token,
                Long id,
                String name,
                String email,
                Role role) {

            this.success = success;
            this.message = message;
            this.token=token;
            this.id = id;
            this.name = name;
            this.email = email;
            this.role = role;
        }

        public boolean isSuccess() {
            return success;
        }

        public String getMessage() {
            return message;
        }

        public Long getId() {
            return id;
        }

        public String getName() {
            return name;
        }

        public String getEmail() {
            return email;
        }

        public Role getRole() {
            return role;
        }

        public String getToken() {
            return token;
        }
    }
}