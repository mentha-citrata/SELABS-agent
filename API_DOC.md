# 接口文档

本文档根据 `core/src/main/java/com/njuse/crsmis/core/controller` 下的 controller 源码整理，按模块汇总接口名称、参数和返回格式。

## 统一返回格式

大多数接口使用统一返回体 `Result<T>`：

- `code`：状态码，`0` 表示成功
- `msg`：提示信息，成功时通常为 `success`
- `data`：业务数据

特殊返回：

- 图片或文件下载接口使用 `ResponseEntity<byte[]>` 或 `ResponseEntity<InputStreamResource>`
- 部分接口直接返回文件流，不再包裹 `Result`

## 1. 权限管理

基础路径：`/v1/authority-management`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 按条件获取用户列表 | GET | `/get-user-list` | `pageNo: long`，`pageSize: long`，`searchDTO: AuthoritySearchDTO` | `Result<List<UserRoleListVO>>` |
| 获取用户数量 | GET | `/get-user-count` | `searchDTO: AuthoritySearchDTO` | `Result<Long>` |
| 修改用户角色 | PUT | `/change-role` | `userId: List<Long>`，`role: List<Long>` | `Result<Void>` |
| 通过 Excel 批量插入用户角色 | POST | `/insert-user-role-by-excel` | `file: MultipartFile` | `Result<Void>` |
| 添加角色 | POST | `/add-role` | `roleName: String`，`roleDesc: String` | `Result<Void>` |
| 获取角色列表 | GET | `/get-role-list` | 无 | `Result<List<RoleInfoVO>>` |
| 删除角色 | DELETE | `/delete-role` | `roleId: long` | `Result<Void>` |
| 添加角色权限 | POST | `/add-role-authority` | `roleId: long`，`authorityId: List<Long>` | `Result<Void>` |
| 删除角色权限 | DELETE | `/delete-role-authority` | `roleId: long`，`authorityId: long` | `Result<Void>` |
| 获取角色权限列表 | GET | `/get-role-authority-list` | `roleId: long` | `Result<List<String>>` |
| 获取权限对应角色列表 | GET | `/get-authority-role-list` | `authorityId: long` | `Result<List<String>>` |
| 获取权限列表 | GET | `/get-authority-list` | 无 | `Result<List<AuthorityVO>>` |
| 根据角色获取权限列表 | GET | `/get-authority-list-by-role` | `roleId: long` | `Result<List<AuthorityVO>>` |
| 获取权限模板 | GET | `/get-excel-template` | 无 | `ResponseEntity<InputStreamResource>` |
| 修改角色权限 | POST | `/edit-role-authority` | `roleId: long`，`authorityId: List<Long>` | `Result<Void>` |

## 2. 教室管理

基础路径：`/v1/classroom`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 添加教室 | POST | `/add-room` | `classroomFromVO: ClassroomFromVO`（body） | `Result<Boolean>` |
| 更新教室信息 | PUT | `/update-room` | `classroomFromVO: ClassroomFromVO`（body），`roomId: Long` | `Result<Boolean>` |
| 删除教室 | DELETE | `/delete-room` | `roomId: Long` | `Result<Boolean>` |
| 获取教室列表 | GET | `/get-classroom-list` | `pageNo: Long`，`pageSize: Long` | `Result<List<ClassroomVO>>` |
| 获取教室数量 | GET | `/get-classroom-count` | 无 | `Result<Long>` |

## 3. 配置中心

基础路径：`/v1/config`

### 3.1 设备配置

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 添加设备 | POST | `/equipment/add` | `name: String`，`totalCount: Integer` | `Result<Void>` |
| 批量添加设备 | POST | `/equipment/batch-add` | `equipmentList: List<EquipmentVO>`（body） | `Result<String>` |
| 更新设备 | PUT | `/equipment/update` | `equipment: EquipmentVO` | `Result<Void>` |
| 删除设备 | DELETE | `/equipment/delete/{id}` | `id: long`（path） | `Result<Void>` |
| 批量删除设备 | DELETE | `/equipment/batch-delete` | `idList: List<Long>` | `Result<Void>` |
| 获取设备列表 | GET | `/equipment/get-equipments` | `pageNo: Integer`，`pageSize: Integer`，`query: String?`，`minCount: Integer?`，`maxCount: Integer?` | `Result<List<EquipmentVO>>` |
| 获取设备数量 | GET | `/equipment/get-equipments-count` | `query: String?`，`minCount: Integer?`，`maxCount: Integer?` | `Result<Integer>` |

### 3.2 耗材配置

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 获取耗材列表 | GET | `/consumable/get-consumables` | `pageNo: Long`，`pageSize: Long`，`query: String?`，`minCount: Integer?`，`maxCount: Integer?` | `Result<List<ConsumableVO>>` |
| 获取耗材数量 | GET | `/consumable/get-consumables-count` | `query: String?`，`minCount: Integer?`，`maxCount: Integer?` | `Result<Integer>` |
| 获取单个耗材 | GET | `/consumable/get-consumable` | `id: Long` | `Result<ConsumableVO>` |
| 添加耗材 | POST | `/consumable/add-consumable` | `request: ConsumableCreateDTO`（body） | `Result<Boolean>` |
| 批量插入耗材 | POST | `/consumable/batch-insert-consumable` | `requestList: List<ConsumableCreateDTO>`（body） | `Result<String>` |
| 修改耗材 | PUT | `/consumable/modify-consumable` | `id: Long`，`newName: String?`，`newCount: Integer?`，`newInfo: String?` | `Result<Boolean>` |
| 删除耗材 | DELETE | `/consumable/delete-consumable` | `id: Long` | `Result<Boolean>` |
| 批量删除耗材 | DELETE | `/consumable/batch-delete-consumable` | `idList: List<Long>` | `Result<String>` |

## 4. 教室预约

基础路径：`/v1/classroom-reservation`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 获取教室状态 | GET | `/get-room-status` | `roomId: long`，`startDate: String?`，`days: int?` | `Result<List<ClassroomStatusVO>>` |
| 获取教室列表 | GET | `/get-room-list` | `classroomSearchDTO: ClassroomSearchDTO`，`pageNo: long?`，`pageSize: long?` | `Result<List<ClassroomStatusVO>>` |
| 获取教室总数 | GET | `/get-room-count` | `classroomSearchDTO: ClassroomSearchDTO` | `Result<Long>` |
| 预约教室 | POST | `/reserve-room` | `classroomReservationFromVO: ClassroomReservationFromVO`（body） | `Result<Long>` |
| 取消预约 | DELETE | `/cancel-reservation` | `userId: Long`，`reservationId: Long` | `Result<Void>` |
| 长期预约教室 | POST | `/reserve-room-long-term` | `classroomLongTermReservationFormVO: ClassroomLongTermReservationFormVO`（body） | `Result<Long>` |
| 获取教室预约记录 | GET | `/get-room-reservation` | `userId: long`，`pageNo: long?`，`pageSize: long?` | `Result<List<ClassroomReservationVO>>` |
| 获取教室预约记录总数 | GET | `/get-room-reservation-count` | `userId: long` | `Result<Long>` |
| 按预约 ID 获取记录 | GET | `/get-room-reservation-by-id` | `reservationId: long` | `Result<ClassroomReservationVO>` |

## 5. 数据中心

基础路径：`/v1/data_center`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 获取用户设备 | GET | `/get_user_device` | `user_id: long` | `Result<List<DeviceBriefVO>>` |
| 获取设备详情 | GET | `/get_device_info` | `device_id: long` | `Result<DeviceDetailedVO>` |
| 获取设备列表 | GET | `/get_devices` | `caseId: int?`，`type: List<String>?`，`userId: long?` | `Result<List<DeviceBasicVO>>` |

## 6. 设备借用

基础路径：`/v1/equipment-borrowing`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 申请借用设备 | POST | `/apply` | `equipmentBorrowingApply: EquipmentBorrowingApplyVO`（body） | `Result<Void>` |
| 获取未归还记录 | GET | `/unreturned` | `pageNo: int`，`pageSize: int`，`userId: long` | `Result<List<EquipmentBorrowingRecordVO>>` |
| 获取进行中记录 | GET | `/processing` | `pageNo: int`，`pageSize: int`，`userId: long` | `Result<List<EquipmentBorrowingRecordVO>>` |
| 获取已完成记录 | GET | `/finished` | `pageNo: int`，`pageSize: int`，`userId: long` | `Result<List<EquipmentBorrowingRecordVO>>` |
| 归还设备 | PUT | `/return` | `userId: long`，`applicationId: long` | `Result<Void>` |
| 撤回申请 | PUT | `/withdraw` | `userId: long`，`applicationId: long` | `Result<Void>` |
| 获取借用详情 | GET | `/detail/{id}` | `id: long`（path） | `Result<EquipmentBorrowingDetailVO>` |
| 审批借用申请 | POST | `/approve` | `equipmentBorrowingApprove: EquipmentBorrowingApproveVO`（body） | `Result<Void>` |
| 经办人批准借出 | PUT | `/operate/borrow` | `applicationId: long` | `Result<Void>` |
| 经办人批准归还 | PUT | `/operate/return` | `applicationId: long` | `Result<Void>` |
| 获取未归还数量 | GET | `/count/unreturned/{userId}` | `userId: long`（path） | `Result<Integer>` |
| 获取进行中数量 | GET | `/count/processing/{userId}` | `userId: long`（path） | `Result<Integer>` |
| 获取已完成数量 | GET | `/count/finished/{userId}` | `userId: long`（path） | `Result<Integer>` |
| 按状态获取记录 | GET | `/record` | `pageNo: int?`，`pageSize: int?`，`status: String[]?` | `Result<List<EquipmentBorrowingRecordVO>>` |
| 按状态获取记录数 | GET | `/count/record` | `status: String[]?` | `Result<Integer>` |
| 获取可借用设备 | GET | `/borrowable-equipment` | 无 | `Result<List<EquipmentVO>>` |

## 7. 报修管理

基础路径：`/v1/repair`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 发起报修 | POST | `/submit` | `submitInfo: SubmitRepairVO`，`images: MultipartFile[]` | `Result<Void>` |
| 分页获取个人报修记录 | GET | `/get-record-paged` | `pageNo: int`，`pageSize: int`，`status: String[]?`，`beginTime: String?`，`endTime: String?` | `Result<List<RepairRecordVO>>` |
| 获取个人报修记录数 | GET | `/record/count` | `status: String[]?`，`beginTime: String?`，`endTime: String?` | `Result<Integer>` |
| 获取全部报修记录数 | GET | `/record/all-count` | `status: String[]?`，`beginTime: String?`，`endTime: String?` | `Result<Integer>` |
| 分页获取全部报修记录 | GET | `/get-all-record-paged` | `pageNo: int`，`pageSize: int`，`status: String[]?`，`beginTime: String?`，`endTime: String?` | `Result<List<RepairRecordVO>>` |
| 处理报修 | POST | `/handle` | `handleInfo: HandleRepairVO`，`images: MultipartFile[]` | `Result<Void>` |
| 获取报修记录图片 | GET | `/record-imgs/{recordId}` | `recordId: long`（path） | `Result<List<String>>` |
| 获取报修结果图片 | GET | `/result-imgs/{resultId}` | `resultId: long`（path） | `Result<List<String>>` |
| 获取报修结果 | GET | `/result/{recordId}` | `recordId: long`（path） | `Result<List<RepairResultVO>>` |
| 获取报修记录详情 | GET | `/record/{recordId}` | `recordId: long`（path） | `Result<RepairRecordVO>` |
| 撤回报修 | PUT | `/withdraw/{recordId}` | `recordId: long`（path） | `Result<Void>` |
| 反馈已解决 | PUT | `/feedback/solved` | `recordId: long` | `Result<Void>` |
| 反馈未解决 | POST | `/feedback/unsolved` | `recordId: long`，`resultId: long`，`feedback: String`，`images: MultipartFile[]` | `Result<Void>` |
| 获取报修反馈 | GET | `/feedback/{recordId}` | `recordId: long`（path） | `Result<List<RepairFeedbackVO>>` |
| 获取反馈图片 | GET | `/feedback-imgs/{feedbackId}` | `feedbackId: long`（path） | `Result<List<String>>` |

## 8. 机位预约

基础路径：`/v1/reservation`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 获取所有房间名称 | GET | `/get-room-names` | 无 | `Result<List<String>>` |
| 添加房间 | POST | `/add-room` | `roomName: String` | `Result<Boolean>` |
| 删除房间 | DELETE | `/delete-room` | `roomName: String` | `Result<Boolean>` |
| 添加机位 | POST | `/add-seat` | `seatName: String`，`roomName: String`，`x: Double`，`y: Double` | `Result<Boolean>` |
| 删除机位 | DELETE | `/delete-seat` | `seatId: Long` | `Result<Boolean>` |
| 获取房间内机位状态 | GET | `/get-seats-by-room-name` | `roomName: String`，`userId: Long` | `Result<List<RoomSeatsStatusVO>>` |
| 获取机位所有预约信息 | GET | `/get-reservations-by-seat` | `seatId: Long` | `Result<List<SeatReservationInfoVO>>` |
| 获取用户预约信息 | GET | `/get-user-reservations` | `userId: Long`，`pageNo: Long?`，`pageSize: Long?` | `Result<List<SeatReservationInfoVO>>` |
| 获取用户预约数量 | GET | `/get-user-reservation-count` | `userId: Long` | `Result<Long>` |
| 获取时间段内可用机位 | GET | `/get-available-seats-by-time` | `startTime: String`，`endTime: String`，`roomName: String?` | `Result<List<SeatStatusVO>>` |
| 预约机位 | POST | `/reserve-seat` | `seatReservationVO: SeatReservationVO`（body） | `Result<Long>` |
| 取消预约 | DELETE | `/cancel-reservation` | `reservationId: Long`，`userId: Long` | `Result<Boolean>` |
| 更新机位状态 | PUT | `/update-seat-status` | `userId: Long`，`seatId: Long`，`newStatus: String` | `Result<Boolean>` |
| 获取预约状态 | GET | `/get-reservation-status` | `reservationId: Long?` | `Result<ReservationStatusVO>` |

## 9. 用户管理

基础路径：`/v1/user`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 用户注册 | POST | `/register` | `registerVO: RegisterVO`（body） | `Result<Void>` |
| 用户登录 | GET | `/login` | `loginVO: LoginVO` | `Result<SaTokenInfo>` |
| 修改用户角色 | PUT | `/role` | `userNumber: String`，`role: int` | `Result<Void>` |
| 退出登录 | DELETE | `/logout` | 无 | `Result<Void>` |
| 按学工号获取用户信息 | GET | `/info/user-number/{userNumber}` | `userNumber: String`（path） | `Result<UserVO>` |
| 按用户 ID 获取用户信息 | GET | `/info/id/{userId}` | `userId: long`（path） | `Result<UserInfoVO>` |
| 更新用户信息 | PUT | `/info` | `newUserInfo: EditUserInfoVO`（body） | `Result<Void>` |
| 模糊搜索用户 | GET | `/search-user` | `query: String` | `Result<List<UserSearchingBoxVO>>` |
| 获取用户导师信息 | GET | `/get-user-mentor` | `userId: Long` | `Result<UserBasicVO>` |
| 按模板导入用户信息 | POST | `/excel/insert-user-with-template` | `templateFile: MultipartFile` | `Result<String>` |
| 获取用户导入模板文件 | GET | `/excel/get-excel-template-file` | 无 | `ResponseEntity<InputStreamResource>` |
| 更新用户导师 | PUT | `/update-user-mentor` | `userId: Long`，`mentorId: Long` | `Result<Void>` |
| 删除用户导师信息 | DELETE | `/delete-user-mentor` | `userId: Long` | `Result<Void>` |
| 重置用户密码 | PUT | `/reset-password` | `userNumber: String` | `Result<Void>` |

## 10. 工位管理

基础路径：`/v1/workstation`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 获取工位信息 | GET | `/get-workstations` | `pageNo: Long?`，`pageSize: Long?`，`studentName: String?`，`studentNumber: String?`，`studentGrade: Integer?`，`studentDegree: String?`，`studentMajor: String?`，`mentorName: String?`，`office: String?`，`workstationNumber: String?` | `Result<List<WorkstationVO>>` |
| 获取工位数量 | GET | `/get-workstations-count` | `studentName: String?`，`studentNumber: String?`，`studentGrade: Integer?`，`studentDegree: String?`，`studentMajor: String?`，`mentorName: String?`，`office: String?`，`workstationNumber: String?` | `Result<Long>` |
| 按学生 ID 获取工位 | GET | `/getWorkstationByUserId` | `userId: Long` | `Result<WorkstationVO>` |
| 添加工位 | POST | `/add` | `workstationFormVO: WorkstationFormVO`（body） | `Result<Boolean>` |
| 修改工位信息 | PUT | `/modify` | `workstationId: Long`，`studentId: Long?`，`office: String?`，`workstationNumber: String?` | `Result<Boolean>` |
| 删除工位 | DELETE | `/delete` | `workstationId: Long` | `Result<Boolean>` |
| 获取 Excel 模板链接 | GET | `/get-excel-template` | 无 | `Result<String>` |
| Excel 导入工位 | POST | `/import-with-excel-template` | `templateFile: MultipartFile` | `Result<String>` |
| 导出 Excel | GET | `/export-excel` | `userId: Long`，`workstationIdList: List<Long>?` | `Result<String>` |
| 导出 Excel 流 | GET | `/export-excel-stream` | `userId: Long`，`workstationIdList: List<Long>?`，`ignoreColumns: List<String>?` | `ResponseEntity<InputStreamResource>` |
| 设置临时 Excel 过期时间 | PUT | `/set-expiration-time` | `expirationDays: Integer` | `Result<Void>` |
| 获取用户最近导出文件 | GET | `/get-user-recent-excels` | `userId: Long` | `Result<List<ExcelUrlVO>>` |
| 获取 Excel 模板文件 | GET | `/get-excel-template-file` | 无 | `ResponseEntity<InputStreamResource>` |

## 11. 统计

基础路径：`/v1/statistics`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 获取工位总数 | GET | `/workstation/get-all-workstations-count` | 无 | `Result<Long>` |
| 获取已完成耗材领用数 | GET | `/consumable/get-finished-collections` | 无 | `Result<Long>` |
| 获取耗材列表 | GET | `/consumable/get-consumables` | 无 | `Result<List<ConsumableVO>>` |
| 获取可预约机位总数 | GET | `/reservation/get-all-available-seat-count` | 无 | `Result<Long>` |
| 获取已借用设备数 | GET | `/equipment-borrowing/get-equipment-borrowed-count` | 无 | `Result<Integer>` |
| 获取设备列表 | GET | `/equipment-borrowing/get-equipments` | 无 | `Result<List<EquipmentVO>>` |
| 获取各角色用户数 | GET | `/user/get-role-count` | 无 | `Result<List<RoleCountVO>>` |
| 获取未维修报修数 | GET | `/repair/get-unrepaired-record-count` | 无 | `Result<Integer>` |
| 获取被占用教室 | GET | `/classroom/get-occupied-classroom` | 无 | `Result<List<ClassroomVO>>` |
| 获取空闲教室 | GET | `/classroom/get-free-classroom` | 无 | `Result<List<ClassroomVO>>` |
| 获取教室使用情况 | GET | `/classroom/get-classroom-usage` | 无 | `Result<List<ClassroomUsageVO>>` |
| 获取数据中心设备数 | GET | `/data-center/get-device-count` | 无 | `Result<Integer>` |
| 获取模块申请数量 | GET | `/data-center/get-application-count` | 无 | `Result<ApplicationCountVO>` |
| 获取未处理巡查问题数 | GET | `/inspect/unhandled` | 无 | `Result<Integer>` |

## 12. 巡查

基础路径：`/v1/inspect`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 获取巡查记录列表 | GET | `/records` | 无 | `Result<List<InspectRecordVO>>` |
| 分页获取巡查记录 | GET | `/getRecordsByPage` | `pageSize: Integer`，`pageNo: Integer` | `Result<List<InspectRecordVO>>` |
| 获取巡查记录统计 | GET | `/recordsCount` | 无 | `Result<InspectCountVO>` |
| 按日期获取巡查记录 | GET | `/getRecordsByDate` | `startDate: String?`，`endDate: String?` | `Result<List<InspectRecordVO>>` |
| 按 ID 获取巡查记录 | GET | `/getRecordById` | `id: Long` | `Result<InspectRecordVO>` |
| 新增巡查记录 | POST | `/addRecord` | `date: String`，`time: String`，`location: String`，`inspector_user_id: Long`，`is_problem_found: Boolean`，`is_problem_solved: Boolean`，`problem_description: String?`，`handler_user_id: Long?`，`handling_description: String?` | `Result<Long>` |
| 处理巡查问题 | POST | `/handleProblem` | `record_id: Long`，`handler_user_id: Long`，`description: String` | `Result<InspectHandlingVO>` |
| 修改巡查记录 | PUT | `/modifyRecord` | `old_id: Long`，`user_id: Long`，`new_is_problem_found: Boolean`，`new_is_problem_solved: Boolean`，`is_problem_changed: Boolean`，`is_handling_changed: Boolean`，`new_location: String?`，`new_inspector_user_id: Long?`，`new_problem: String?`，`new_handler_user_id: Long?`，`new_handling_description: String?` | `Result<Long>` |
| 删除巡查记录 | DELETE | `/deleteRecord` | `id: Long`，`user_id: Long` | `Result<Long>` |
| 获取单条更新记录 | GET | `/update/getUpdate` | `id: Long` | `Result<InspectUpdateVO>` |
| 获取更新记录列表 | GET | `/update/getUpdates` | 无 | `Result<List<InspectUpdateVO>>` |
| 分页获取更新记录 | GET | `/update/getUpdatesByPage` | `pageSize: Integer`，`pageNo: Integer` | `Result<List<InspectUpdateVO>>` |
| 获取记录更新历史 | GET | `/update/history` | `id: Long` | `Result<List<InspectHistoryVO>>` |

## 13. 耗材领用

基础路径：`/v1/consumable`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 获取授权二维码图片 | GET | `/get-authorize-code-img` | `userId: Long`，`frontEndUrl: String` | `ResponseEntity<byte[]>` |
| 创建授权码 | POST | `/create-authorize-key` | `userId: Long`，`expireTime: String` | `Result<Void>` |
| 获取授权 URL | GET | `/get-authorize-url` | `userId: Long`，`frontEndUrl: String` | `Result<String>` |
| 删除授权码 | DELETE | `/delete-authorize-key` | `userId: Long` | `Result<Void>` |
| 添加耗材领用申请 | POST | `/add-request` | `request: CollectRequestFormVO`（body） | `Result<Long>` |
| 获取用户待处理领用申请 | GET | `/get-user-pending-requests` | `userId: Long` | `Result<List<CollectRecordVO>>` |
| 拒绝领用申请 | DELETE | `/reject-request` | `userId: Long`，`requestId: Long` | `Result<Void>` |
| 自主批准领用 | POST | `/authorize-collection-request` | `form: AutoAuthorizeCollectFormVO`（body） | `Result<String>` |
| 经办人批准领用 | POST | `/authorize-request-by-transactor` | `form: AutoAuthorizeCollectFormVO`（body） | `Result<String>` |
| 获取领用记录 | GET | `/get-collect-records` | `pageNo: Long`，`pageSize: Long`，`userId: Long?`，`transactorId: Long?`，`minCollectTime: String?`，`maxCollectTime: String?`，`itemName: String?`，`status: String?` | `Result<List<CollectRecordVO>>` |
| 获取领用记录数 | GET | `/get-collect-records-count` | `userId: Long?`，`transactorId: Long?`，`minCollectTime: String?`，`maxCollectTime: String?`，`itemName: String?`，`status: String?` | `Result<Long>` |
| 撤回领用申请 | DELETE | `/withdraw-request` | `userId: Long`，`recordId: Long` | `Result<Void>` |

## 14. 申请模块

### 14.1 数据中心进入申请

基础路径：`/v1/application/data-center`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 添加申请 | POST | `/add-application` | `application: DataCenterEntryApplicationFormVO`（body） | `Result<Long>` |
| 获取申请详情 | GET | `/get-application` | `applicationId: Long` | `Result<DataCenterEntryApplicationVO>` |
| 按条件获取申请列表 | GET | `/get-applications-by-condition` | `searchCondition: ApplicationSearchConditionVO` | `Result<List<DataCenterEntryApplicationVO>>` |
| 按条件获取申请数量 | GET | `/get-application-count-by-condition` | `searchCondition: ApplicationSearchConditionVO` | `Result<Long>` |

### 14.2 服务器修改申请

基础路径：`/v1/application/server-modification`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 添加申请 | POST | `/modify-server` | `serverModificationApplicationFormVO: ServerModificationApplicationFormVO`（body） | `Result<Long>` |
| 获取申请详情 | GET | `/get-application` | `applicationId: Long` | `Result<ServerModificationApplicationVO>` |
| 按条件获取申请列表 | GET | `/get-applications-by-condition` | `searchCondition: ApplicationSearchConditionVO` | `Result<List<ServerModificationApplicationSimpleVO>>` |
| 按条件获取申请数量 | GET | `/get-application-count-by-condition` | `searchCondition: ApplicationSearchConditionVO` | `Result<Long>` |

### 14.3 服务器注册申请

基础路径：`/v1/application/server-registry`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 添加申请 | POST | `/add-server` | `serverRegistryApplicationFormVO: ServerRegistryApplicationFormVO`（body） | `Result<Long>` |
| 获取申请详情 | GET | `/get-application` | `applicationId: Long` | `Result<ServerRegistryApplicationVO>` |
| 按条件获取申请列表 | GET | `/get-applications-by-condition` | `searchConditionVO: ApplicationSearchConditionVO` | `Result<List<ServerRegistryApplicationSimpleVO>>` |
| 按条件获取申请数量 | GET | `/get-application-count-by-condition` | `searchCondition: ApplicationSearchConditionVO` | `Result<Long>` |

## 15. 审批模块

### 15.1 数据中心审批

基础路径：`/v1`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 获取审批信息 | GET | `/approval/data-center/get-approval` | `approvalId: Long` | `Result<SimpleApprovalVO>` |
| 审批 | POST | `/approval/data-center/approve` | `formVO: SimpleApprovalFormVO`（body） | `Result<Long>` |
| 批量审批 | POST | `/approval/data-center/batch-approve` | `userId: Long`，`applicationIdList: List<Long>` | `Result<List<Long>>` |
| 按申请 ID 获取审批信息 | GET | `/approval/data-center/get-approval-by-application-id` | `applicationId: Long` | `Result<SimpleApprovalVO>` |

### 15.2 服务器修改审批

基础路径：`/v1/approval/data-center/server-modification`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 审批 | POST | `/approve` | `formVO: SimpleApprovalFormVO`（body） | `Result<Long>` |
| 按申请 ID 获取审批信息 | GET | `/get-approval-by-application-id` | `applicationId: Long` | `Result<SimpleApprovalVO>` |

### 15.3 服务器注册审批

基础路径：`/v1/approval/data-center/server-registry`

| 接口名称 | 方法 | 路径 | 参数 | 返回格式 |
| --- | --- | --- | --- | --- |
| 审批 | POST | `/approve` | `formVO: ServerRegistryApprovalFormVO`（body） | `Result<Long>` |
| 按申请 ID 获取审批信息 | GET | `/get-approval-by-application-id` | `applicationId: Long` | `Result<ServerRegistryApprovalVO>` |

## 16. 备注

- 部分接口使用 `@SaCheckPermission` 做权限控制，前端对接时需要携带登录态并确保权限满足。
- 少数接口参数没有显式使用 `@RequestParam` 或 `@RequestBody`，Spring 会按默认绑定规则处理。
- 带文件流的接口建议前端直接按下载接口处理，不要再包一层 JSON 解析。
