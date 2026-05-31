package com.counselai.backend.controller;

import com.counselai.backend.entity.College;
import com.counselai.backend.entity.Cutoff;
import com.counselai.backend.repository.CollegeRepository;
import com.counselai.backend.repository.CutoffRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/colleges")
@CrossOrigin(origins = "*")
public class CollegeController {

    @Autowired
    private CollegeRepository collegeRepository;

    @Autowired
    private CutoffRepository cutoffRepository;

    // GET all colleges
    @GetMapping
    public List<College> getAllColleges() {
        return collegeRepository.findAll();
    }

    // GET college by ID
    @GetMapping("/{id}")
    public ResponseEntity<College> getCollegeById(@PathVariable Long id) {
        return collegeRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // GET search colleges by name
    @GetMapping("/search")
    public List<College> searchColleges(@RequestParam String query) {
        return collegeRepository.findByNameContainingIgnoreCaseOrderByNameAsc(query);
    }

    // GET distinct districts
    @GetMapping("/districts")
    public List<String> getDistricts() {
        return collegeRepository.findDistinctDistricts();
    }

    // GET colleges by district
    @GetMapping("/district/{district}")
    public List<College> getCollegesByDistrict(@PathVariable String district) {
        // Will be sorted on the frontend or we could sort here.
        return collegeRepository.findByDistrict(district);
    }

    // GET cutoffs for a college
    @GetMapping("/{id}/cutoffs")
    public List<Cutoff> getCollegeCutoffs(@PathVariable Long id) {
        return cutoffRepository.findByCollegeIdOrderByYearDesc(id);
    }

    // POST add new college (for testing)
    @PostMapping
    public College addCollege(@RequestBody College college) {
        return collegeRepository.save(college);
    }

    // Health check
    @GetMapping("/health")
    public String health() {
        return "CounselAI Backend is running!";
    }
}