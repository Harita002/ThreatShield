package com.threatshield.backend.test;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/analyst")
public class AnalystTestController {

    @GetMapping("/dashboard")
    public String analystDashboard() {
        return "Welcome Analyst! You have ANALYST access.";
    }
}