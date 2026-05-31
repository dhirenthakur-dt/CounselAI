package com.counselai.backend.repository;

import com.counselai.backend.entity.Cutoff;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface CutoffRepository extends JpaRepository<Cutoff, Long> {

    // Get cutoffs for a specific college and branch
    List<Cutoff> findByCollegeIdAndBranchId(Long collegeId, Long branchId);

    // Get cutoffs by category and year
    List<Cutoff> findByCategoryAndYear(String category, Integer year);

    // Get all cutoffs for a specific college
    List<Cutoff> findByCollegeIdOrderByYearDesc(Long collegeId);

    // THE MOST IMPORTANT QUERY
    // Find all colleges where student percentile >= closing percentile
    @Query("""
        SELECT c FROM Cutoff c
        WHERE c.category = :category
        AND c.year = :year
        AND c.capRound = :capRound
        AND c.closingPercentile <= :studentPercentile
        ORDER BY c.closingPercentile DESC
        """)
    List<Cutoff> findEligibleColleges(
        @Param("studentPercentile") Double studentPercentile,
        @Param("category") String category,
        @Param("year") Integer year,
        @Param("capRound") Integer capRound
    );
}