package com.counselai.backend.service;

import org.springframework.stereotype.Service;
import java.util.*;

@Service
public class RankingService {

    public List<Map<String, Object>> rankColleges(
            List<Map<String, Object>> eligibleColleges,
            String priority) {

        for (Map<String, Object> college : eligibleColleges) {

            double totalScore = 0;

            // --- FACTOR 1: Safety Margin Score (30%) ---
            double safetyMargin = (double) college.get("safetyMargin");
            double safetyScore;
            if (safetyMargin >= 5.0)      safetyScore = 30;
            else if (safetyMargin >= 3.0) safetyScore = 24;
            else if (safetyMargin >= 1.0) safetyScore = 18;
            else                          safetyScore = 10;

            // --- FACTOR 2: NAAC Grade Score (20%) ---
            String naacGrade = (String) college.get("naacGrade");
            double naacScore = switch (naacGrade != null ? naacGrade : "") {
                case "A++" -> 20;
                case "A+"  -> 17;
                case "A"   -> 14;
                case "B++" -> 11;
                case "B+"  -> 8;
                default    -> 5;
            };

            // --- FACTOR 3: Fee Score (20%) ---
            Integer annualFee = (Integer) college.get("annualFee");
            double feeScore;
            if (annualFee == null)          feeScore = 10;
            else if (annualFee <= 30000)    feeScore = 20;
            else if (annualFee <= 80000)    feeScore = 16;
            else if (annualFee <= 120000)   feeScore = 12;
            else if (annualFee <= 180000)   feeScore = 8;
            else                            feeScore = 4;

            // --- FACTOR 4: Hostel Score (15%) ---
            Boolean hostel = (Boolean) college.get("hostelAvailable");
            double hostelScore = (hostel != null && hostel) ? 15 : 8;

            // --- FACTOR 5: College Type Score (15%) ---
            // Government colleges score higher (lower fees, better infrastructure)
            String collegeName = (String) college.get("collegeName");
            double typeScore;
            if (collegeName != null && (
                collegeName.contains("Government") ||
                collegeName.contains("COEP") ||
                collegeName.contains("VJTI") ||
                collegeName.contains("WCE") ||
                collegeName.contains("SGGS") ||
                collegeName.contains("GECA"))) {
                typeScore = 15;
            } else {
                typeScore = 10;
            }

            totalScore = safetyScore + naacScore + feeScore + hostelScore + typeScore;

            // Adjust weights if student said placement matters more
            if ("placement".equalsIgnoreCase(priority)) {
                // Boost NAAC score for placement proxy
                totalScore += naacScore * 0.3;
            }

            // Round to 1 decimal
            totalScore = Math.round(totalScore * 10.0) / 10.0;

            college.put("totalScore", totalScore);
            college.put("scoreBreakdown", Map.of(
                "safetyScore", safetyScore,
                "naacScore", naacScore,
                "feeScore", feeScore,
                "hostelScore", hostelScore,
                "typeScore", typeScore
            ));
        }

        // Sort by totalScore descending
        eligibleColleges.sort((a, b) ->
            Double.compare((double) b.get("totalScore"),
                           (double) a.get("totalScore"))
        );

        // Add rank number
        for (int i = 0; i < eligibleColleges.size(); i++) {
            eligibleColleges.get(i).put("rank", i + 1);
        }

        return eligibleColleges;
    }
}