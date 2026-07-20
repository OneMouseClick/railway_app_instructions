package com.railway.gateway.domain.entity;

import com.railway.gateway.domain.enums.TaskStatus;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.SuperBuilder;

@Entity
@Table(name = "tasks")
@Getter
@Setter
@SuperBuilder
@NoArgsConstructor
@AllArgsConstructor
public class Task extends BaseUuidEntity {

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "original_file_name", nullable = false, length = 500)
    private String originalFileName;

    @Column(name = "original_file_type", nullable = false, length = 255)
    private String originalFileType;

    @Column(name = "minio_object_name", nullable = false, length = 500)
    private String minioObjectName;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 50)
    @lombok.Builder.Default
    private TaskStatus status = TaskStatus.CREATED;

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;

    @Column(name = "result_minio_object_name", length = 500)
    private String resultMinioObjectName;

    @Column(name = "parsed_content_object_key", length = 500)
    private String parsedContentObjectKey;

    @Column(name = "generated_instruction_object_key", length = 500)
    private String generatedInstructionObjectKey;
}