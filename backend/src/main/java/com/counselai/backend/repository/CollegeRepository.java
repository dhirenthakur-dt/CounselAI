package com.counselai.backend.repository;

import com.counselai.backend.entity.College;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface CollegeRepository extends JpaRepository<College, Long> {

    List<College> findByDistrict(String district);

    List<College> findByNaacGrade(String naacGrade);

    List<College> findByNameContainingIgnoreCaseOrderByNameAsc(String name);

    @org.springframework.data.jpa.repository.Query("SELECT DISTINCT c.district FROM College c WHERE c.district IS NOT NULL ORDER BY c.district")
    List<String> findDistinctDistricts();
}