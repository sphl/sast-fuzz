; ModuleID = 'sum.bc'
source_filename = "llvm-link"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@.str = private unnamed_addr constant [9 x i8] c"Sum = %d\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 !dbg !7 {
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  store i32 0, i32* %1, align 4
  call void @llvm.dbg.declare(metadata i32* %2, metadata !11, metadata !DIExpression()), !dbg !12
  call void @llvm.dbg.declare(metadata i32* %3, metadata !13, metadata !DIExpression()), !dbg !14
  call void @llvm.dbg.declare(metadata i32* %4, metadata !15, metadata !DIExpression()), !dbg !16
  store i32 0, i32* %4, align 4, !dbg !16
  store i32 17, i32* %2, align 4, !dbg !17
  store i32 1, i32* %3, align 4, !dbg !18
  br label %5, !dbg !20

5:                                                ; preds = %13, %0
  %6 = load i32, i32* %3, align 4, !dbg !21
  %7 = load i32, i32* %2, align 4, !dbg !23
  %8 = icmp sle i32 %6, %7, !dbg !24
  br i1 %8, label %9, label %16, !dbg !25

9:                                                ; preds = %5
  %10 = load i32, i32* %3, align 4, !dbg !26
  %11 = load i32, i32* %4, align 4, !dbg !28
  %12 = add nsw i32 %11, %10, !dbg !28
  store i32 %12, i32* %4, align 4, !dbg !28
  br label %13, !dbg !29

13:                                               ; preds = %9
  %14 = load i32, i32* %3, align 4, !dbg !30
  %15 = add nsw i32 %14, 1, !dbg !30
  store i32 %15, i32* %3, align 4, !dbg !30
  br label %5, !dbg !31, !llvm.loop !32

16:                                               ; preds = %5
  %17 = load i32, i32* %4, align 4, !dbg !35
  %18 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([9 x i8], [9 x i8]* @.str, i64 0, i64 0), i32 %17), !dbg !36
  ret i32 0, !dbg !37
}

; Function Attrs: nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

declare dso_local i32 @printf(i8*, ...) #2

attributes #0 = { noinline nounwind optnone uwtable "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" "unsafe-fp-math"="false" "use-soft-float"="false" }

!llvm.dbg.cu = !{!0}
!llvm.ident = !{!3}
!llvm.module.flags = !{!4, !5, !6}

!0 = distinct !DICompileUnit(language: DW_LANG_C99, file: !1, producer: "clang version 12.0.0", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !2, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "sum.c", directory: "/tmp/tmp.iYdQWh7z89/tests/artifacts")
!2 = !{}
!3 = !{!"clang version 12.0.0"}
!4 = !{i32 7, !"Dwarf Version", i32 4}
!5 = !{i32 2, !"Debug Info Version", i32 3}
!6 = !{i32 1, !"wchar_size", i32 4}
!7 = distinct !DISubprogram(name: "main", scope: !1, file: !1, line: 5, type: !8, scopeLine: 5, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !2)
!8 = !DISubroutineType(types: !9)
!9 = !{!10}
!10 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!11 = !DILocalVariable(name: "n", scope: !7, file: !1, line: 6, type: !10)
!12 = !DILocation(line: 6, column: 9, scope: !7)
!13 = !DILocalVariable(name: "i", scope: !7, file: !1, line: 6, type: !10)
!14 = !DILocation(line: 6, column: 12, scope: !7)
!15 = !DILocalVariable(name: "sum", scope: !7, file: !1, line: 6, type: !10)
!16 = !DILocation(line: 6, column: 15, scope: !7)
!17 = !DILocation(line: 11, column: 7, scope: !7)
!18 = !DILocation(line: 13, column: 12, scope: !19)
!19 = distinct !DILexicalBlock(scope: !7, file: !1, line: 13, column: 5)
!20 = !DILocation(line: 13, column: 10, scope: !19)
!21 = !DILocation(line: 13, column: 17, scope: !22)
!22 = distinct !DILexicalBlock(scope: !19, file: !1, line: 13, column: 5)
!23 = !DILocation(line: 13, column: 22, scope: !22)
!24 = !DILocation(line: 13, column: 19, scope: !22)
!25 = !DILocation(line: 13, column: 5, scope: !19)
!26 = !DILocation(line: 14, column: 16, scope: !27)
!27 = distinct !DILexicalBlock(scope: !22, file: !1, line: 13, column: 30)
!28 = !DILocation(line: 14, column: 13, scope: !27)
!29 = !DILocation(line: 15, column: 5, scope: !27)
!30 = !DILocation(line: 13, column: 25, scope: !22)
!31 = !DILocation(line: 13, column: 5, scope: !22)
!32 = distinct !{!32, !25, !33, !34}
!33 = !DILocation(line: 15, column: 5, scope: !19)
!34 = !{!"llvm.loop.mustprogress"}
!35 = !DILocation(line: 17, column: 24, scope: !7)
!36 = !DILocation(line: 17, column: 5, scope: !7)
!37 = !DILocation(line: 18, column: 5, scope: !7)
