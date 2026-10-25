package com.threatshield.backend.ml;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.beans.factory.annotation.Value;
import java.io.IOException;

@Service
public class MlService {

    private final RestTemplate restTemplate;

//     private static final String FASTAPI_URL =
//             "http://127.0.0.1:8000";
        @Value("${ml.service.url:http://127.0.0.1:8000}")
        private String fastApiUrl;

    public MlService() {
        this.restTemplate = new RestTemplate();
    }

    // ============================================================
    // CSV ANALYSIS
    // ============================================================

    public String analyzeDataset(
            MultipartFile file) throws IOException {

        String url =
                fastApiUrl + "/analyze";

        ByteArrayResource resource =
                new ByteArrayResource(file.getBytes()) {

                    @Override
                    public String getFilename() {
                        return file.getOriginalFilename();
                    }
                };

        MultiValueMap<String, Object> body =
                new LinkedMultiValueMap<>();

        body.add("file", resource);

        HttpHeaders headers =
                new HttpHeaders();

        headers.setContentType(
                MediaType.MULTIPART_FORM_DATA
        );

        HttpEntity<MultiValueMap<String, Object>> request =
                new HttpEntity<>(
                        body,
                        headers
                );

        ResponseEntity<String> response =
                restTemplate.postForEntity(
                        url,
                        request,
                        String.class
                );

        return response.getBody();
    }

    // ============================================================
// SINGLE EMPLOYEE EXPLANATION
// ============================================================

public String explainEmployee(Object employee) {

    String url =
            fastApiUrl + "/explain";

    HttpHeaders headers =
            new HttpHeaders();

    headers.setContentType(
            MediaType.APPLICATION_JSON
    );

    HttpEntity<Object> request =
            new HttpEntity<>(
                    employee,
                    headers
            );

    ResponseEntity<String> response =
            restTemplate.postForEntity(
                    url,
                    request,
                    String.class
            );

    return response.getBody();
}
}