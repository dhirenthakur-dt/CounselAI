package com.counselai.backend.service;

import com.counselai.backend.entity.Cutoff;
import com.counselai.backend.repository.CutoffRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.*;

@Service
public class EligibilityService {

    @Autowired
    private CutoffRepository cutoffRepository;

    public List<Map<String, Object>> findEligibleColleges(
            Double percentile,
            String category,
            Integer year,
            Integer capRound) {

        List<Cutoff> cutoffs = cutoffRepository.findEligibleColleges(
            percentile, category, year, capRound
        );

        List<Map<String, Object>> result = new ArrayList<>();

        for (Cutoff c : cutoffs) {

            // Calculate safety margin
            double safetyMargin = percentile - c.getClosingPercentile().doubleValue();

            // Determine chance level
            String chance;
            if (safetyMargin >= 3.0) {
                chance = "HIGH";
            } else if (safetyMargin >= 1.0) {
                chance = "MEDIUM";
            } else {
                chance = "LOW";
            }

            Map<String, Object> entry = new LinkedHashMap<>();
            entry.put("collegeId", c.getCollege().getId());
            entry.put("collegeName", c.getCollege().getName());
            entry.put("district", c.getCollege().getDistrict());
            entry.put("branchName", c.getBranch() != null ? c.getBranch().getBranchName() : "N/A");
            entry.put("annualFee", c.getCollege().getAnnualFee());
            entry.put("naacGrade", c.getCollege().getNaacGrade());
            entry.put("hostelAvailable", c.getCollege().getHostelAvailable());
            entry.put("closingPercentile", c.getClosingPercentile());
            entry.put("yourPercentile", percentile);
            entry.put("safetyMargin", Math.round(safetyMargin * 100.0) / 100.0);
            entry.put("chance", chance);
            entry.put("category", category);

            result.add(entry);
        }

        return result;
    }
}