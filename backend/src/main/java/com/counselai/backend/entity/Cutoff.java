package com.counselai.backend.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;

@Entity
@Table(name = "cutoffs")
@Data
public class Cutoff {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "college_id", nullable = false)
    private College college;

    @ManyToOne
    @JoinColumn(name = "branch_id")
    private Branch branch;

    @Column(nullable = false)
    private Integer year;

    @Column(nullable = false)
    private Integer capRound;

    @Column(nullable = false)
    private String category;

    private String seatType;
    private BigDecimal openingPercentile;
    private BigDecimal closingPercentile;
    private Integer openingRank;
    private Integer closingRank;
}