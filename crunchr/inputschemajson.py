inputschema = """
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "title": "input.json schema",
    "properties": {
        "input": {
            "type": "array",
            "items": {
                "oneOf": [
                    {
                        "properties": {
                            "system_id": {
                                "type": "string"
                            },
                            "job_id": {
                                "type": "string"
                            },
                            "units_processed": {
                                "type": "integer"
                            },
                            "units_failed": {
                                "type": "integer"
                            }
                        },
                        "required": [
                            "system_id",
                            "job_id",
                            "units_processed",
                            "units_failed"
                        ],
                        "additionalProperties": false
                    },
                    {
                        "properties": {
                            "get_stats": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "get_stats"
                        ],
                        "additionalProperties": false
                    }
                ]
            }
        }
    },
    "required": [
        "input"
    ]
}
"""
