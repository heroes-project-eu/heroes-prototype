from fastapi import Body

### For Custom Examples and responses of APIs

decide_response = {
    "dismissed_clusters": [
        {
            "main_cluster": "Too many nodes failures",
        }
    ],
    "ranking": [
        [
        {
            "cluster": "main_cluster",
            "rank": 1,
            "input": "{'JobName': 'dummy', 'Requested_Memory': 2, 'Requested_Cores': 2, 'Timelimit': 10, 'Application': 'openfoam', 'Partition': 'test', 'QOS': 1, 'Account': 'default', 'Cluster': 'heroes', 'Cust_Input_Size': 30636747, 'Cust_HEROES_ORGANIZATION_ID': 1, 'Cust_HEROES_ORGANIZATION_NAME': 'ucit', 'Cust_HEROES_TEMPLATE_WORKFLOW_ID': 1, 'Cust_HEROES_USER_ID': 0}",
            "predictions": {
            "cost": 0,
            "time": 473,
            "energy": 2000000
            },
            "confidence": {
            "cost": 0.66,
            "time": 0.55,
            "energy": 0.63
            },
            "units": {
            "time": "seconds",
            "energy": "joules",
            "cost": "EUR"
            }
        },
        ]
    ],
    "predicted_resources": {
        "main_cluster": {
        "timelimit": [
            {
            "input": "{'JobName': 'dummy', 'Requested_Memory': 2, 'Requested_Cores': 2, 'Timelimit': 10, 'Application': 'openfoam', 'Partition': 'test', 'QOS': 1, 'Account': 'default', 'Cluster': 'heroes', 'Cust_Input_Size': 30636747, 'Cust_HEROES_ORGANIZATION_ID': 1, 'Cust_HEROES_ORGANIZATION_NAME': 'ucit', 'Cust_HEROES_TEMPLATE_WORKFLOW_ID': 1, 'Cust_HEROES_USER_ID': 0}",
            "prediction": "02m 25s",
            "prediction_num": 145,
            "prediction_unit": "seconds",
            "confidence": 0.66
            }
        ],
        "memory": [
            {
            "input": "{'JobName': 'dummy', 'Requested_Memory': 2, 'Requested_Cores': 2, 'Timelimit': 10, 'Application': 'openfoam', 'Partition': 'test', 'QOS': 1, 'Account': 'default', 'Cluster': 'heroes', 'Cust_Input_Size': 30636747, 'Cust_HEROES_ORGANIZATION_ID': 1, 'Cust_HEROES_ORGANIZATION_NAME': 'ucit', 'Cust_HEROES_TEMPLATE_WORKFLOW_ID': 1, 'Cust_HEROES_USER_ID': 0}",
            "prediction": "2.0 GB",
            "prediction_num": 2147483648,
            "prediction_unit": "bytes",
            "confidence": 0.95
            }
        ]
        },
    }
}

# Exemples input parameters for submit examples
examples_body = Body(
            ...,
            examples={
                "workflow level": {
                    "summary": "A Worfklow parameters example (Workflow level)",
                    "description": "CPU, memory (Byte) and time (Second) for the full workflow",
                    "value": {
                        "workflow_name": "dummy_workflow",
                        "workflow_input_dir": "/basicuser/wf1-input",
                        "workflow_placement": {"cluster": "main_cluster"},
                        "workflow_parameters": {
                            "cpus": "1",
                            "memory": "1024",
                            "time":"3600"
                        }
                    },
                },
                "task level": {
                    "summary": "A Workflow with Task parameters example (Task level)",
                    "description": "CPU, memory (Byte) and time (Second) for each task by name",
                    "value": {
                        "workflow_name": "dummy_workflow",
                        "workflow_input_dir": "/basicuser/wf1-input",
                        "workflow_placement": {"cluster": "second_cluster"},
                        "workflow_parameters": {
                            "SplitLetters": {"cpus": "1"}, 
                            "ConvertToUpper": {"cpus": "1"},
                        },
                    },
                },
            },
        )