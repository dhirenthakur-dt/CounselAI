package com.counselai.backend.controller;

import com.counselai.backend.entity.DocumentRequired;
import com.counselai.backend.repository.DocumentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/api/documents")
@CrossOrigin(origins = "*")
public class DocumentController {

    @Autowired
    private DocumentRepository documentRepository;

    // Get checklist for a category
    @GetMapping("/checklist")
    public Map<String, Object> getChecklist(
            @RequestParam String category) {

        List<DocumentRequired> docs =
            documentRepository.findDocumentsForCategory(category);

        // Separate mandatory and optional
        List<Map<String, Object>> mandatory = new ArrayList<>();
        List<Map<String, Object>> optional  = new ArrayList<>();
        List<String> warnings               = new ArrayList<>();

        for (DocumentRequired doc : docs) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("documentName", doc.getDocumentName());
            item.put("category", doc.getCategory());
            item.put("notes", doc.getNotes());

            if (Boolean.TRUE.equals(doc.getIsMandatory())) {
                mandatory.add(item);
            } else {
                optional.add(item);
            }

            // Add warning if notes contain CRITICAL
            if (doc.getNotes() != null &&
                doc.getNotes().toUpperCase().contains("CRITICAL")) {
                warnings.add("⚠️ " + doc.getDocumentName()
                    + ": " + doc.getNotes());
            }
        }

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("category", category);
        response.put("totalDocuments", docs.size());
        response.put("mandatoryCount", mandatory.size());
        response.put("mandatory", mandatory);
        response.put("optional", optional);
        response.put("warnings", warnings);

        return response;
    }

    // Get all available categories
    @GetMapping("/categories")
    public List<String> getCategories() {
        return List.of(
            "GOPENS - General Open",
            "GOBCS - OBC",
            "GSCS - SC",
            "GSTS - ST",
            "EWS - Economically Weaker Section"
        );
    }
}