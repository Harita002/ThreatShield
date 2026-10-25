package com.threatshield.backend.controller;

import com.threatshield.backend.ml.MlService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/analysis")
@CrossOrigin(origins = "http://localhost:5173")
public class AnalysisController {

    private final MlService mlService;

    public AnalysisController(MlService mlService) {
        this.mlService = mlService;
    }

    // ============================================================
    // ANALYZE DATASET
    // ============================================================

    @PostMapping("/analyze")
    public ResponseEntity<?> analyzeDataset(
            @RequestParam("file") MultipartFile file) {

                 System.out.println(">>> AnalysisController reached");

        try {

            if (file.isEmpty()) {

                return ResponseEntity
                        .badRequest()
                        .body("Please upload a CSV file.");
            }

            String result =
                    mlService.analyzeDataset(file);

            return ResponseEntity.ok(result);

        } catch (Exception e) {

            return ResponseEntity
                    .internalServerError()
                    .body(
                        "Unable to analyze dataset: "
                        + e.getMessage()
                    );
        }
    }

    // ============================================================
// SINGLE EMPLOYEE EXPLANATION
// ============================================================

@PostMapping("/explain")
public ResponseEntity<?> explainEmployee(
        @RequestBody Object employee) {

    try {

        String result =
                mlService.explainEmployee(employee);

        return ResponseEntity.ok(result);

    } catch (Exception e) {

        return ResponseEntity
                .internalServerError()
                .body(
                    "Unable to generate explanation: "
                    + e.getMessage()
                );
    }
}
}
