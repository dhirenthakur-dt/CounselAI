package com.counselai.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "documents_required")
@Data
public class DocumentRequired {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String category;

    @Column(nullable = false)
    private String documentName;

    private Boolean isMandatory;

    private String notes;
}