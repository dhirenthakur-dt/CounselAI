package com.counselai.backend.repository;

import com.counselai.backend.entity.DocumentRequired;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface DocumentRepository extends JpaRepository<DocumentRequired, Long> {

    // Get documents for specific category
    List<DocumentRequired> findByCategory(String category);

    // Get ALL documents + category-specific together
    // For OBC student → return ALL + GOBCS documents
    @Query("""
        SELECT d FROM DocumentRequired d
        WHERE d.category = 'ALL'
        OR d.category = :category
        ORDER BY d.isMandatory DESC, d.category ASC
        """)
    List<DocumentRequired> findDocumentsForCategory(
        @Param("category") String category
    );
}