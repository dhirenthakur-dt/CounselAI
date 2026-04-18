package com.counselai.backend.controller;

import com.counselai.backend.entity.College;
import com.counselai.backend.repository.CollegeRepository;
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