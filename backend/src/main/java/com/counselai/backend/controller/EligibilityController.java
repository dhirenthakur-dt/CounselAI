package com.counselai.backend.controller;

import com.counselai.backend.service.EligibilityService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/eligibility")
@CrossOrigin(origins = "*")
public class EligibilityController {

    @Autowired
    private EligibilityService eligibilityService;

    @GetMapping("/check")
    public List<Map<String, Object>> checkEligibility(
            @RequestParam Double percentile,
            @RequestParam String category,
            @RequestParam(defaultValue = "2024") Integer year,
            @RequestParam(defaultValue = "1") Integer capRound) {

        return eligibilityService.findEligibleColleges(
            percentile, category, year, capRound
        );
    }
}