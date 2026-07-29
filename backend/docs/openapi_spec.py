"""OpenAPI 3.0 specification for the Business Development Web App API."""

SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Business Development Web App API",
        "description": (
            "RESTful API for managing users, clients, services, "
            "service categories, client-service assignments, and "
            "aggregated dashboard statistics for a business "
            "development platform.\n\n"
            "## Authentication\n"
            "All protected endpoints require a valid JWT Bearer token "
            "obtained via the `/api/users/login` endpoint.\n\n"
            "## Authorization\n"
            "Endpoints are protected by role-based access control (RBAC):\n"
            "- **admin**: Full access to all endpoints.\n"
            "- **manager**: Access to clients, services, categories, "
            "assignments, and dashboard (read/write).\n"
            "- **employee**: Read-only access to clients, services, "
            "categories, and assignments."
        ),
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "email": "support@example.com"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5001",
            "description": "Local development server"
        }
    ],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": (
                    "JWT access token obtained from `/api/users/login`. "
                    "Include in the `Authorization` header as: "
                    "`Bearer <token>`"
                )
            }
        },
        "schemas": {
            "SuccessResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "message": {
                        "type": "string",
                        "example": "Operation successful"
                    },
                    "data": {
                        "description": "Response payload"
                    }
                },
                "required": ["success", "message"]
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": False
                    },
                    "message": {
                        "type": "string",
                        "example": "Error description"
                    }
                },
                "required": ["success", "message"]
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "full_name": {
                        "type": "string",
                        "example": "John Doe"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "example": "john@example.com"
                    },
                    "phone": {
                        "type": "string",
                        "example": "+1234567890"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["admin", "manager", "employee"],
                        "example": "employee"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive"],
                        "example": "active"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time"
                    }
                }
            },
            "Client": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "company_name": {
                        "type": "string",
                        "example": "Acme Corp"
                    },
                    "contact_person": {
                        "type": "string",
                        "example": "Jane Smith"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "example": "jane@acme.com"
                    },
                    "phone": {
                        "type": "string",
                        "example": "+1234567890"
                    },
                    "address": {
                        "type": "string",
                        "example": "123 Main St, City, Country"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["lead", "prospect", "customer"],
                        "example": "lead"
                    }
                }
            },
            "ServiceCategory": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "name": {
                        "type": "string",
                        "example": "Consulting"
                    },
                    "description": {
                        "type": "string",
                        "example": "Professional consulting services"
                    }
                }
            },
            "Service": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "category_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "name": {
                        "type": "string",
                        "example": "Strategy Consulting"
                    },
                    "description": {
                        "type": "string",
                        "example": "Strategic business consulting"
                    },
                    "price": {
                        "type": "number",
                        "format": "decimal",
                        "example": 5000.00
                    },
                    "duration_days": {
                        "type": "integer",
                        "example": 30
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive"],
                        "example": "active"
                    }
                }
            },
            "ClientServiceAssignment": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 1
                    },
                    "client_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "service_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2024-01-01T00:00:00"
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2024-01-31T23:59:59"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled"],
                        "example": "pending"
                    }
                }
            },
            "LoginRequest": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {
                        "type": "string",
                        "format": "email",
                        "example": "admin@example.com"
                    },
                    "password": {
                        "type": "string",
                        "format": "password",
                                "example": "123456"
                    }
                }
            },
            "LoginResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "message": {
                        "type": "string",
                        "example": "Login successful"
                    },
                    "data": {
                        "type": "object",
                        "properties": {
                            "access_token": {
                                "type": "string",
                                "description": "JWT access token"
                            },
                            "user": {
                                "$ref": "#/components/schemas/User"
                            }
                        }
                    }
                }
            },
            "CreateUserRequest": {
                "type": "object",
                "required": ["full_name", "email", "password"],
                "properties": {
                    "full_name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 100,
                        "example": "John Doe"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "maxLength": 150,
                        "example": "john@example.com"
                    },
                    "password": {
                        "type": "string",
                        "format": "password",
                        "minLength": 8,
                        "example": "securepass123"
                    },
                    "phone": {
                        "type": "string",
                        "pattern": "^\\+?[0-9]{10,15}$",
                        "example": "+1234567890"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["admin", "manager", "employee"],
                        "default": "employee",
                        "example": "employee"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive"],
                        "default": "active",
                        "example": "active"
                    }
                }
            },
            "UpdateUserRequest": {
                "type": "object",
                "properties": {
                    "full_name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 100
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "maxLength": 150
                    },
                    "phone": {
                        "type": "string",
                        "pattern": "^\\+?[0-9]{10,15}$"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["admin", "manager", "employee"]
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive"]
                    }
                }
            },
            "ChangePasswordRequest": {
                "type": "object",
                "required": ["new_password"],
                "properties": {
                    "new_password": {
                        "type": "string",
                        "format": "password",
                        "minLength": 8,
                        "example": "newsecurepass123"
                    }
                }
            },
            "CreateClientRequest": {
                "type": "object",
                "required": ["company_name", "contact_person"],
                "properties": {
                    "company_name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 150,
                        "example": "Acme Corp"
                    },
                    "contact_person": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 100,
                        "example": "Jane Smith"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "maxLength": 150,
                        "example": "jane@acme.com"
                    },
                    "phone": {
                        "type": "string",
                        "pattern": "^\\+?[0-9]{10,15}$",
                        "example": "+1234567890"
                    },
                    "address": {
                        "type": "string",
                        "maxLength": 1000,
                        "example": "123 Main St, City, Country"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["lead", "prospect", "customer"],
                        "default": "lead",
                        "example": "lead"
                    }
                }
            },
            "UpdateClientRequest": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 150
                    },
                    "contact_person": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 100
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "maxLength": 150
                    },
                    "phone": {
                        "type": "string",
                        "pattern": "^\\+?[0-9]{10,15}$"
                    },
                    "address": {
                        "type": "string",
                        "maxLength": 1000
                    },
                    "status": {
                        "type": "string",
                        "enum": ["lead", "prospect", "customer"]
                    }
                }
            },
            "ChangeClientStatusRequest": {
                "type": "object",
                "required": ["status"],
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["lead", "prospect", "customer"],
                        "example": "customer"
                    }
                }
            },
            "CreateServiceRequest": {
                "type": "object",
                "required": ["name", "category_id"],
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 150,
                        "example": "Strategy Consulting"
                    },
                    "category_id": {
                        "type": "integer",
                        "minimum": 1,
                        "example": 1
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 1000,
                        "example": "Strategic business consulting"
                    },
                    "price": {
                        "type": "number",
                        "format": "decimal",
                        "minimum": 0,
                        "example": 5000.00
                    },
                    "duration_days": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 3650,
                        "example": 30
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive"],
                        "default": "active",
                        "example": "active"
                    }
                }
            },
            "UpdateServiceRequest": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 150
                    },
                    "category_id": {
                        "type": "integer",
                        "minimum": 1
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 1000
                    },
                    "price": {
                        "type": "number",
                        "format": "decimal",
                        "minimum": 0
                    },
                    "duration_days": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 3650
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive"]
                    }
                }
            },
            "CreateCategoryRequest": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 100,
                        "example": "Consulting"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 1000,
                        "example": "Professional consulting services"
                    }
                }
            },
            "UpdateCategoryRequest": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 100
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 1000
                    }
                }
            },
            "AssignServiceRequest": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "ISO 8601 format (YYYY-MM-DDTHH:MM:SS)",
                        "example": "2024-01-01T00:00:00"
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "ISO 8601 format (YYYY-MM-DDTHH:MM:SS)",
                        "example": "2024-01-31T23:59:59"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled"],
                        "default": "pending",
                        "example": "pending"
                    }
                }
            },
            "UpdateAssignmentRequest": {
                "type": "object",
                "properties": {
                    "client_id": {
                        "type": "integer",
                        "minimum": 1
                    },
                    "service_id": {
                        "type": "integer",
                        "minimum": 1
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled"]
                    }
                }
            },
            "DashboardStatistics": {
                "type": "object",
                "properties": {
                    "total_users": {
                        "type": "integer",
                        "example": 25
                    },
                    "total_clients": {
                        "type": "integer",
                        "example": 120
                    },
                    "total_services": {
                        "type": "integer",
                        "example": 15
                    },
                    "total_categories": {
                        "type": "integer",
                        "example": 8
                    },
                    "recent_clients": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Client"
                        },
                        "description": "Up to 5 most recent clients"
                    },
                    "recent_services": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Service"
                        },
                        "description": "Up to 5 most recent services"
                    }
                }
            }
        },
        "responses": {
            "Unauthorized": {
                "description": "Authentication required or invalid token",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse"
                        },
                        "examples": {
                            "NoToken": {
                                "summary": "Missing token",
                                "value": {
                                    "success": False,
                                    "message": "Authorization token is required"
                                }
                            },
                            "InvalidToken": {
                                "summary": "Invalid token",
                                "value": {
                                    "success": False,
                                    "message": "Invalid token"
                                }
                            },
                            "ExpiredToken": {
                                "summary": "Expired token",
                                "value": {
                                    "success": False,
                                    "message": "Token has expired"
                                }
                            }
                        }
                    }
                }
            },
            "Forbidden": {
                "description": "Insufficient permissions for this action",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse"
                        },
                        "example": {
                            "success": False,
                            "message": "Access denied. Admin or manager role required."
                        }
                    }
                }
            },
            "NotFound": {
                "description": "Requested resource not found",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse"
                        },
                        "example": {
                            "success": False,
                            "message": "Resource not found"
                        }
                    }
                }
            },
            "ValidationError": {
                "description": "Validation error in request body",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse"
                        },
                        "example": {
                            "success": False,
                            "message": "Email is required"
                        }
                    }
                }
            },
            "InternalServerError": {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse"
                        },
                        "example": {
                            "success": False,
                            "message": "Internal server error"
                        }
                    }
                }
            }
        }
    },
    "tags": [
        {
            "name": "Authentication",
            "description": "User login, logout, and session management"
        },
        {
            "name": "Users",
            "description": "User account management (admin only)"
        },
        {
            "name": "Clients",
            "description": "Client records management"
        },
        {
            "name": "Services",
            "description": "Service catalog management"
        },
        {
            "name": "Service Categories",
            "description": "Service category management"
        },
        {
            "name": "Client Service Assignments",
            "description": "Assign services to clients"
        },
        {
            "name": "Dashboard",
            "description": "Aggregated statistics and reporting"
        }
    ],
    "paths": {
        "/api/users/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Authenticate a user",
                "description": (
                    "Validates user credentials and returns a JWT "
                    "access token. The token must be included in the "
                    "`Authorization` header for all protected endpoints."
                ),
                "operationId": "login",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/LoginRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Login successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LoginResponse"
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "description": "Invalid credentials",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                },
                                "example": {
                                    "success": False,
                                    "message": "Invalid email or password"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/users/logout": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Logout current user",
                "description": (
                    "Revokes the current JWT access token. "
                    "The token will no longer be valid for subsequent requests."
                ),
                "operationId": "logout",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Logout successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Logout successful"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "500": {
                        "$ref": "#/components/responses/InternalServerError"
                    }
                }
            }
        },
        "/api/users/me": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Get current authenticated user",
                "description": (
                    "Returns the profile of the currently "
                    "authenticated user based on the JWT token."
                ),
                "operationId": "getCurrentUser",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "User retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "User retrieved successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/User"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            }
        },
        "/api/users/": {
            "get": {
                "tags": ["Users"],
                "summary": "Get all users",
                "description": "Retrieves a list of all users. Admin only.",
                "operationId": "getAllUsers",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Users retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Users retrieved successfully"},
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/User"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            },
            "post": {
                "tags": ["Users"],
                "summary": "Create a new user",
                "description": "Creates a new user account. Admin only.",
                "operationId": "createUser",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/CreateUserRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "User created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "User created successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/User"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            }
        },
        "/api/users/{user_id}": {
            "get": {
                "tags": ["Users"],
                "summary": "Get a user by ID",
                "description": "Retrieves a single user by their ID. Admin only.",
                "operationId": "getUserById",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "User unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "User retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "User retrieved successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/User"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            },
            "put": {
                "tags": ["Users"],
                "summary": "Update a user",
                "description": "Updates an existing user's profile. Admin only.",
                "operationId": "updateUser",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "User unique identifier"
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UpdateUserRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "User updated successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "User updated successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/User"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            },
            "delete": {
                "tags": ["Users"],
                "summary": "Delete a user",
                "description": "Permanently deletes a user account. Admin only.",
                "operationId": "deleteUser",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "User unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "User deleted successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "User deleted successfully"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            }
        },
        "/api/users/{user_id}/password": {
            "put": {
                "tags": ["Users"],
                "summary": "Change a user's password",
                "description": "Sets a new password for the specified user. Admin only.",
                "operationId": "changePassword",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "User unique identifier"
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ChangePasswordRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Password changed successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Password changed successfully"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            }
        },
        "/api/users/{user_id}/activate": {
            "put": {
                "tags": ["Users"],
                "summary": "Activate a user account",
                "description": (
                    "Sets the user's status to `active`. "
                    "Admin only."
                ),
                "operationId": "activateUser",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "User unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "User activated successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "User activated successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/User"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            }
        },
        "/api/users/{user_id}/deactivate": {
            "put": {
                "tags": ["Users"],
                "summary": "Deactivate a user account",
                "description": (
                    "Sets the user's status to `inactive`. "
                    "Admin only."
                ),
                "operationId": "deactivateUser",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "User unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "User deactivated successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "User deactivated successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/User"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            }
        },
        "/api/clients/": {
            "get": {
                "tags": ["Clients"],
                "summary": "Get all clients",
                "description": "Retrieves a list of all clients. Any authenticated user.",
                "operationId": "getAllClients",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Clients retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Clients retrieved successfully"},
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/Client"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    }
                }
            },
            "post": {
                "tags": ["Clients"],
                "summary": "Create a new client",
                "description": "Creates a new client record. Admin or Manager only.",
                "operationId": "createClient",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/CreateClientRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Client created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Client created successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/Client"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            }
        },
        "/api/clients/{client_id}": {
            "get": {
                "tags": ["Clients"],
                "summary": "Get a client by ID",
                "description": "Retrieves a single client. Any authenticated user.",
                "operationId": "getClientById",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Client unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Client retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Client retrieved successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/Client"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            },
            "put": {
                "tags": ["Clients"],
                "summary": "Update a client",
                "description": "Updates an existing client. Admin or Manager only.",
                "operationId": "updateClient",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Client unique identifier"
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UpdateClientRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Client updated successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Client updated successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/Client"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            },
            "delete": {
                "tags": ["Clients"],
                "summary": "Delete a client",
                "description": "Permanently deletes a client. Admin only.",
                "operationId": "deleteClient",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Client unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Client deleted successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Client deleted successfully"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            }
        },
        "/api/clients/{client_id}/status": {
            "put": {
                "tags": ["Clients"],
                "summary": "Change a client's status",
                "description": (
                    "Updates the status of a client (lead, prospect, "
                    "or customer). Admin or Manager only."
                ),
                "operationId": "changeClientStatus",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Client unique identifier"
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ChangeClientStatusRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Client status changed successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Client status changed successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/Client"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            }
        },
        "/api/services/": {
            "get": {
                "tags": ["Services"],
                "summary": "Get all services",
                "description": "Retrieves a list of all services. Any authenticated user.",
                "operationId": "getAllServices",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Services retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Services retrieved successfully"},
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/Service"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    }
                }
            },
            "post": {
                "tags": ["Services"],
                "summary": "Create a new service",
                "description": "Creates a new service. Admin or Manager only.",
                "operationId": "createService",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/CreateServiceRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Service created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Service created successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/Service"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            }
        },
        "/api/services/{service_id}": {
            "get": {
                "tags": ["Services"],
                "summary": "Get a service by ID",
                "description": "Retrieves a single service. Any authenticated user.",
                "operationId": "getServiceById",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "service_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Service unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Service retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Service retrieved successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/Service"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            },
            "put": {
                "tags": ["Services"],
                "summary": "Update a service",
                "description": "Updates an existing service. Admin or Manager only.",
                "operationId": "updateService",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "service_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Service unique identifier"
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UpdateServiceRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Service updated successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Service updated successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/Service"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            },
            "delete": {
                "tags": ["Services"],
                "summary": "Delete a service",
                "description": "Permanently deletes a service. Admin or Manager only.",
                "operationId": "deleteService",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "service_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Service unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Service deleted successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Service deleted successfully"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            }
        },
        "/api/services/category/{category_id}": {
            "get": {
                "tags": ["Services"],
                "summary": "Get services by category",
                "description": (
                    "Retrieves all services belonging to the "
                    "specified category. Any authenticated user."
                ),
                "operationId": "getServicesByCategory",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "category_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Category unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Services retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Services retrieved successfully"},
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/Service"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            }
        },
        "/api/service-categories/": {
            "get": {
                "tags": ["Service Categories"],
                "summary": "Get all service categories",
                "description": "Retrieves a list of all service categories. Any authenticated user.",
                "operationId": "getAllCategories",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Categories retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Categories retrieved successfully"},
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/ServiceCategory"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    }
                }
            },
            "post": {
                "tags": ["Service Categories"],
                "summary": "Create a new service category",
                "description": "Creates a new service category. Admin or Manager only.",
                "operationId": "createCategory",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/CreateCategoryRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Category created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Category created successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/ServiceCategory"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            }
        },
        "/api/service-categories/{category_id}": {
            "get": {
                "tags": ["Service Categories"],
                "summary": "Get a category by ID",
                "description": "Retrieves a single category. Any authenticated user.",
                "operationId": "getCategoryById",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "category_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Category unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Category retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Category retrieved successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/ServiceCategory"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            },
            "put": {
                "tags": ["Service Categories"],
                "summary": "Update a category",
                "description": "Updates an existing category. Admin or Manager only.",
                "operationId": "updateCategory",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "category_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Category unique identifier"
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UpdateCategoryRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Category updated successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Category updated successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/ServiceCategory"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            },
            "delete": {
                "tags": ["Service Categories"],
                "summary": "Delete a category",
                "description": "Permanently deletes a category. Admin or Manager only.",
                "operationId": "deleteCategory",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "category_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Category unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Category deleted successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Category deleted successfully"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            }
        },
        "/api/client-services/client/{client_id}": {
            "get": {
                "tags": ["Client Service Assignments"],
                "summary": "Get all services for a client",
                "description": (
                    "Retrieves all service assignments for the "
                    "specified client. Any authenticated user."
                ),
                "operationId": "getClientServices",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Client unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Client services retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Client services retrieved successfully"},
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/ClientServiceAssignment"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            }
        },
        "/api/client-services/service/{service_id}": {
            "get": {
                "tags": ["Client Service Assignments"],
                "summary": "Get all clients for a service",
                "description": (
                    "Retrieves all client assignments for the "
                    "specified service. Any authenticated user."
                ),
                "operationId": "getServiceClients",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "service_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Service unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Service clients retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Service clients retrieved successfully"},
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/ClientServiceAssignment"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            }
        },
        "/api/client-services/{client_id}/assign/{service_id}": {
            "post": {
                "tags": ["Client Service Assignments"],
                "summary": "Assign a service to a client",
                "description": (
                    "Creates a new assignment linking a service to a client. "
                    "Admin or Manager only."
                ),
                "operationId": "assignService",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Client unique identifier"
                    },
                    {
                        "name": "service_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Service unique identifier"
                    }
                ],
                "requestBody": {
                    "required": False,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/AssignServiceRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Service assigned successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Service assigned successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/ClientServiceAssignment"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            }
        },
        "/api/client-services/{assignment_id}": {
            "put": {
                "tags": ["Client Service Assignments"],
                "summary": "Update a service assignment",
                "description": "Updates an existing assignment. Admin or Manager only.",
                "operationId": "updateAssignment",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "assignment_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Assignment unique identifier"
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UpdateAssignmentRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Assignment updated successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Assignment updated successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/ClientServiceAssignment"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "$ref": "#/components/responses/ValidationError"
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            },
            "delete": {
                "tags": ["Client Service Assignments"],
                "summary": "Remove a service assignment",
                "description": "Permanently removes an assignment. Admin or Manager only.",
                "operationId": "removeAssignment",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "name": "assignment_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Assignment unique identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Assignment removed successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Assignment removed successfully"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    },
                    "404": {
                        "$ref": "#/components/responses/NotFound"
                    }
                }
            }
        },
        "/api/dashboard/statistics": {
            "get": {
                "tags": ["Dashboard"],
                "summary": "Get aggregated dashboard statistics",
                "description": (
                    "Returns aggregated statistics including total users, "
                    "clients, services, categories, assignments, and "
                    "client breakdown by status. Admin or Manager only."
                ),
                "operationId": "getDashboardStatistics",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Dashboard statistics retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {"type": "string", "example": "Dashboard statistics retrieved successfully"},
                                        "data": {
                                            "$ref": "#/components/schemas/DashboardStatistics"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "$ref": "#/components/responses/Unauthorized"
                    },
                    "403": {
                        "$ref": "#/components/responses/Forbidden"
                    }
                }
            }
        }
    }
}
