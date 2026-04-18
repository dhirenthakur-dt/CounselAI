package com.counselai.backend.repository;

import com.counselai.backend.entity.Branch;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface BranchRepository extends JpaRepository<Branch, Long> {

    List<Branch> findByCollegeId(Long collegeId);

    List<Branch> findByBranchCodeIgnoreCase(String branchCode);
}