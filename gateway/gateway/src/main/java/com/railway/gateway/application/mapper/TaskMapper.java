package com.railway.gateway.application.mapper;

import com.railway.gateway.api.dto.CreateTaskResponse;
import com.railway.gateway.api.dto.TaskDetailsResponse;
import com.railway.gateway.api.dto.TaskStatusResponse;
import com.railway.gateway.api.dto.TaskSummaryResponse;
import com.railway.gateway.domain.entity.Task;
import com.railway.gateway.domain.enums.TaskStatus;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

import static org.mapstruct.ReportingPolicy.IGNORE;

@Mapper(componentModel = "spring", unmappedTargetPolicy = IGNORE, imports = {TaskStatus.class})
public interface TaskMapper {

    @Mapping(target = "status", expression = "java(task.getStatus().name())")
    CreateTaskResponse toCreateTaskResponse(Task task);

    @Mapping(target = "status", expression = "java(task.getStatus().name())")
    TaskSummaryResponse toTaskSummaryResponse(Task task);

    @Mapping(target = "status", expression = "java(task.getStatus().name())")
    @Mapping(target = "resultAvailable", expression = "java(task.getStatus() == TaskStatus.COMPLETED)")
    TaskDetailsResponse toTaskDetailsResponse(Task task);

    @Mapping(target = "status", expression = "java(task.getStatus().name())")
    TaskStatusResponse toTaskStatusResponse(Task task);
}