package com.counselai.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "branches")
@Data
public class Branch {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "college_id", nullable = false)
    private College college;

    @Column(nullable = false)
    private String branchName;

    private String branchCode;
    private Integer totalSeats;
}