# self_filter.launch.py
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

import xacro
import re

def remove_comments(text):
    pattern = r'<!--(.*?)-->'
    return re.sub(pattern, '', text, flags=re.DOTALL)

def generate_launch_description():
    

    package_name1 = 'example_description'  # 替换为您的包名
    package_dir1 = get_package_share_directory(package_name1)
    
    package_name2 = 'filter'  # 替换为您的包名
    
    package_dir2 = get_package_share_directory(package_name2)

    default_filter_config = os.path.join(package_dir2, 'params', 'self_filter.yaml')
    
    default_urdf_path = os.path.join(package_dir1, 'urdf', 'example.xacro')  # 替换为您的URDF文件
    
 
    xacro_file = default_urdf_path
    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    
    robot_description_content = doc.toxml()
    
    
    description_name_arg = DeclareLaunchArgument(
        'description_name',
        default_value='/robot_description'
    )
    zero_for_removed_points_arg = DeclareLaunchArgument(
        'zero_for_removed_points',
        default_value='true'
    )
    lidar_sensor_type_arg = DeclareLaunchArgument(
        'lidar_sensor_type',
        default_value='0' #根据激光雷达类型调整   0: 为标准PointCloud2格式
    )
    in_pointcloud_topic_arg = DeclareLaunchArgument(
        'in_pointcloud_topic',
        default_value='/cloud_in' # 修改为自己的点云话题
    )
    out_pointcloud_topic_arg = DeclareLaunchArgument(
        'out_pointcloud_topic',
        default_value='/cloud_out'  # 修改为自己期望的输出话题
    )
    robot_description_arg = DeclareLaunchArgument(
        'robot_description',
        default_value=robot_description_content
    )
    filter_config_arg = DeclareLaunchArgument(
        'filter_config',
        default_value=default_filter_config
    )

    # Create a log action to print the config
    log_config = LogInfo(msg=LaunchConfiguration('filter_config'))

    self_filter_node = Node(
        package='robot_self_filter',
        executable='self_filter',
        name='self_filter',
        output='screen',
        parameters=[
            LaunchConfiguration('filter_config'),  # loads the YAML file
            {
                'lidar_sensor_type': LaunchConfiguration('lidar_sensor_type'),
                'robot_description': ParameterValue(
                    LaunchConfiguration('robot_description'),
                    value_type=str
                ),
                'zero_for_removed_points': LaunchConfiguration('zero_for_removed_points'),
                'use_sim_time': True # 如果使用仿真时间，请设置为True
            }
        ],
        remappings=[
            ('/robot_description', LaunchConfiguration('description_name')),
            ('/cloud_in', LaunchConfiguration('in_pointcloud_topic')),
            ('/cloud_out', LaunchConfiguration('out_pointcloud_topic')),
        ],
    )

    return LaunchDescription([
        description_name_arg,
        zero_for_removed_points_arg,
        lidar_sensor_type_arg,
        in_pointcloud_topic_arg,
        out_pointcloud_topic_arg,
        robot_description_arg,
        filter_config_arg,
        log_config,
        self_filter_node
    ])
