package com.counselai.backend.controller;

import com.counselai.backend.service.EligibilityService;
import com.counselai.backend.service.RankingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/ranking")
@CrossOrigin(origins = "*")
public class RankingController {

    @Autowired
    private EligibilityService eligibilityService;

    @Autowired
    private RankingService rankingService;

    @GetMapping("/ranked-colleges")
    public List<Map<String, Object>> getRankedColleges(
            @RequestParam Double percentile,
            @RequestParam String category,
            @RequestParam(defaultValue = "2024") Integer year,
            @RequestParam(defaultValue = "1") Integer capRound,
            @RequestParam(defaultValue = "general") String priority) {

        // Step 1: Get eligible colleges
        List<Map<String, Object>> eligible =
            eligibilityService.findEligibleColleges(
                percentile, category, year, capRound
            );

        // Step 2: Rank them
        return rankingService.rankColleges(eligible, priority);
    }
}