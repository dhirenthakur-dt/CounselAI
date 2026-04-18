package com.counselai.backend.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "colleges")
@Data
public class College {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    private String district;
    private String city;
    private String collegeType;
    private String naacGrade;
    private Integer nirfRank;
    private Integer annualFee;
    private Boolean hostelAvailable;
    private String website;
    private Integer establishedYear;

    @Column(updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}